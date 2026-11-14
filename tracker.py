"""
PolyTail — alert when Polymarket's most profitable traders pile onto the same bet.

Every run:
  1. Get the watchlist: wallets.json (made by backtest.py, scored on real results)
     if it exists and is recent, otherwise the top of Polymarket's profit leaderboard.
  2. Pull each wallet's open positions.
  3. Group by market + outcome. If enough watched wallets hold the same side,
     that's a consensus signal.
  4. Send new / strengthened signals to Telegram, and log each one to
     signals_log.csv so scorecard.py can grade them once markets settle.

Alert-only: this script never places bets.
"""

import csv
import html
import json
import os
import time
from datetime import datetime, timezone

from common import get_json, money, num, send_telegram

# ---------------------------------------------------------------- settings
# Defaults. Any key in settings.json overrides these (handy after a backtest).
SETTINGS = {
    "LEADERBOARD_PERIODS": ["MONTH", "ALL"],  # fallback watchlist source
    "LEADERBOARD_DEPTH": 100,
    "MIN_PNL": 50_000,               # wallet must be up at least this much ($)
    "MIN_PNL_TO_VOLUME": 0.02,       # profit / volume >= 2% -> drops market makers
    "MIN_POSITION_USD": 1_000,       # ignore small positions
    "MIN_PRICE": 0.05,               # skip near-dead outcomes
    "MAX_PRICE": 0.95,               # skip near-certain outcomes
    "MIN_WALLETS_AGREEING": 3,       # how many watched wallets must share the bet
    "MAX_ALERTS_PER_RUN": 10,
    "WALLETS_FILE_MAX_AGE_DAYS": 21, # ignore wallets.json if older than this
}

STATE_FILE = os.environ.get("POLYTAIL_STATE", "state.json")
LOG_FILE = os.environ.get("POLYTAIL_LOG", "signals_log.csv")
SETTINGS_FILE = os.environ.get("POLYTAIL_SETTINGS", "settings.json")
WALLETS_FILE = os.environ.get("POLYTAIL_WALLETS", "wallets.json")

LOG_FIELDS = ["alerted_at", "kind", "key", "condition_id", "outcome_index", "outcome",
              "title", "event_slug", "price", "avg_entry", "wallets", "total_value",
              "opposing_wallets", "end_date"]


def load_settings():
    s = dict(SETTINGS)
    try:
        with open(SETTINGS_FILE) as f:
            s.update({k: v for k, v in json.load(f).items() if k in SETTINGS})
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return s


# ---------------------------------------------------------------- watchlist
def scored_wallets(cfg):
    """Wallets picked by backtest.py from real track records, if fresh."""
    try:
        with open(WALLETS_FILE) as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    age_days = (time.time() - num(data.get("generated_at"))) / 86400
    if age_days > cfg["WALLETS_FILE_MAX_AGE_DAYS"]:
        print(f"wallets.json is {age_days:.0f} days old — falling back to leaderboard")
        return {}
    return {w["wallet"]: {"name": w.get("name") or w["wallet"][:8], "pnl": num(w.get("pnl"))}
            for w in data.get("wallets", [])}


def leaderboard_wallets(cfg):
    wallets = {}
    for period in cfg["LEADERBOARD_PERIODS"]:
        for offset in range(0, cfg["LEADERBOARD_DEPTH"], 50):
            rows = get_json("/v1/leaderboard", {
                "category": "OVERALL", "timePeriod": period,
                "orderBy": "PNL", "limit": 50, "offset": offset,
            }) or []
            for row in rows:
                w = (row.get("proxyWallet") or "").lower()
                pnl, vol = num(row.get("pnl")), num(row.get("vol"))
                if not w or pnl < cfg["MIN_PNL"]:
                    continue
                if vol > 0 and pnl / vol < cfg["MIN_PNL_TO_VOLUME"]:
                    continue
                if w not in wallets or pnl > wallets[w]["pnl"]:
                    wallets[w] = {"name": row.get("userName") or w[:8], "pnl": pnl}
            if len(rows) < 50:
                break
    return wallets


# ---------------------------------------------------------------- positions
def open_positions(wallet, cfg):
    rows = get_json("/positions", {
        "user": wallet, "sizeThreshold": 1, "limit": 500,
        "sortBy": "CURRENT", "sortDirection": "DESC",
    }) or []
    out, now = [], time.time()
    for p in rows:
        if p.get("redeemable"):
            continue
        value, price = num(p.get("currentValue")), num(p.get("curPrice"))
        if value < cfg["MIN_POSITION_USD"] or not (cfg["MIN_PRICE"] <= price <= cfg["MAX_PRICE"]):
            continue
        end = p.get("endDate")
        if end:
            try:
                end_dt = datetime.fromisoformat(end.replace("Z", "+00:00"))
                if end_dt.tzinfo is None:
                    end_dt = end_dt.replace(tzinfo=timezone.utc)
                if end_dt.timestamp() < now:
                    continue
            except ValueError:
                pass
        out.append(p)
    return out


def find_consensus(wallets, positions_by_wallet, cfg):
    groups = {}
    for w, positions in positions_by_wallet.items():
        for p in positions:
            key = f"{p.get('conditionId')}|{p.get('outcomeIndex')}"
            g = groups.setdefault(key, {
                "key": key,
                "title": p.get("title") or "Unknown market",
                "outcome": p.get("outcome") or "?",
                "event_slug": p.get("eventSlug") or p.get("slug") or "",
                "condition_id": p.get("conditionId"),
                "outcome_index": p.get("outcomeIndex"),
                "price": num(p.get("curPrice")),
                "end_date": (p.get("endDate") or "")[:10],
                "holders": [],
            })
            g["holders"].append({
                "wallet": w, "name": wallets[w]["name"], "trader_pnl": wallets[w]["pnl"],
                "value": num(p.get("currentValue")), "avg_price": num(p.get("avgPrice")),
            })

    signals = []
    for g in groups.values():
        if len(g["holders"]) < cfg["MIN_WALLETS_AGREEING"]:
            continue
        g["holders"].sort(key=lambda h: h["value"], reverse=True)
        g["total_value"] = sum(h["value"] for h in g["holders"])
        shares = sum(h["value"] / g["price"] for h in g["holders"]) if g["price"] else 0
        cost = sum(h["value"] / g["price"] * h["avg_price"] for h in g["holders"]) if g["price"] else 0
        g["avg_entry"] = cost / shares if shares else 0
        signals.append(g)

    by_market = {}
    for g in groups.values():
        by_market.setdefault(g["condition_id"], []).append(g)
    for s in signals:
        s["opposing_wallets"] = sum(len(g["holders"]) for g in by_market[s["condition_id"]]
                                    if g["key"] != s["key"])

    signals.sort(key=lambda s: (len(s["holders"]), s["total_value"]), reverse=True)
    return signals


# ---------------------------------------------------------------- output
def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"alerted": {}}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=1, sort_keys=True)


def log_signal(s, kind):
    new_file = not os.path.exists(LOG_FILE)
    with open(LOG_FILE, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=LOG_FIELDS)
        if new_file:
            w.writeheader()
        w.writerow({
            "alerted_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "kind": kind, "key": s["key"], "condition_id": s["condition_id"],
            "outcome_index": s["outcome_index"], "outcome": s["outcome"], "title": s["title"],
            "event_slug": s["event_slug"], "price": round(s["price"], 4),
            "avg_entry": round(s["avg_entry"], 4), "wallets": len(s["holders"]),
            "total_value": round(s["total_value"], 2),
            "opposing_wallets": s["opposing_wallets"], "end_date": s["end_date"],
        })


def format_alert(s, is_upgrade):
    head = "📈 MORE TOP TRADERS JOINED" if is_upgrade else "🐋 TOP TRADERS AGREE"
    lines = [
        f"<b>{head}</b>",
        f"<b>{html.escape(s['title'])}</b>",
        f"Side: <b>{html.escape(s['outcome'])}</b> @ {s['price']*100:.0f}¢ now"
        f" (their avg entry {s['avg_entry']*100:.0f}¢)",
        f"{len(s['holders'])} top wallets, {money(s['total_value'])} combined",
    ]
    if s["opposing_wallets"]:
        lines.append(f"⚠️ {s['opposing_wallets']} top wallet(s) on the other side")
    if s["end_date"]:
        lines.append(f"Ends: {s['end_date']}")
    lines.append("")
    for h in s["holders"][:6]:
        lines.append(f"• {html.escape(h['name'])} — {money(h['value'])} in"
                     f" (trader P&L {money(h['trader_pnl'])})")
    if len(s["holders"]) > 6:
        lines.append(f"• +{len(s['holders']) - 6} more")
    if s["event_slug"]:
        lines.append(f"\nhttps://polymarket.com/event/{s['event_slug']}")
    return "\n".join(lines)


def main():
    cfg = load_settings()
    state = load_state()
    alerted = state.setdefault("alerted", {})

    wallets = scored_wallets(cfg)
    source = "backtest-scored wallets.json"
    if not wallets:
        wallets, source = leaderboard_wallets(cfg), "leaderboard"
    print(f"Watching {len(wallets)} wallets (from {source})")
    if not wallets:
        print("No wallets returned — API may be down. Exiting without changes.")
        return

    positions = {}
    for w in wallets:
        positions[w] = open_positions(w, cfg)
        time.sleep(0.15)

    signals = find_consensus(wallets, positions, cfg)
    print(f"{len(signals)} consensus signals")

    sent, live_keys = 0, set()
    for s in signals:
        live_keys.add(s["key"])
        prev = alerted.get(s["key"])
        is_upgrade = prev is not None and len(s["holders"]) > prev["wallets"]
        if not (prev is None or is_upgrade) or sent >= cfg["MAX_ALERTS_PER_RUN"]:
            continue
        if send_telegram(format_alert(s, is_upgrade)):
            log_signal(s, "upgrade" if is_upgrade else "new")
            alerted[s["key"]] = {
                "wallets": len(s["holders"]), "title": s["title"], "outcome": s["outcome"],
                "first_seen": (prev or {}).get(
                    "first_seen", datetime.now(timezone.utc).isoformat(timespec="minutes")),
            }
            sent += 1

    for k in list(alerted):  # forget dissolved signals so they can re-alert later
        if k not in live_keys:
            del alerted[k]

    save_state(state)
    print(f"Sent {sent} alert(s)")


if __name__ == "__main__":
    main()
