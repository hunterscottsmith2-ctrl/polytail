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

from common import (american, book_quote, get_json, log_books, log_fill, market_info, money, num, queue_recheck, run_rechecks,
                    send_telegram)

# Two independent tests run from this file:
#   main   (default)               — all markets, overall leaderboards
#   sports (POLYTAIL_PROFILE=sports) — game markets only, sports leaderboards,
#                                     pre-kickoff only, its own log/state/settings
PROFILE = os.environ.get("POLYTAIL_PROFILE", "main")
SUFFIX = "" if PROFILE == "main" else f"_{PROFILE}"

# ---------------------------------------------------------------- settings
# Defaults. Any key in settings.json overrides these (handy after a backtest).
SETTINGS = {
    "CATEGORY": "sports" if PROFILE == "sports" else "overall",
    "SPORTS_GAMES_ONLY": PROFILE == "sports",   # only moneyline/spread/total markets, pre-kickoff
    "LABEL": "🏈 SPORTS: " if PROFILE == "sports" else "",
    # Watchlist = same pool the backtest tested: profit AND volume boards.
    "LEADERBOARDS": [["ALL", "PNL"], ["MONTH", "PNL"], ["ALL", "VOLUME"], ["MONTH", "VOLUME"]],
    "LEADERBOARD_DEPTH": 100,
    "MIN_PNL": -1e12,                # no profit floor (backtest pool had none)
    "MIN_PNL_TO_VOLUME": -1.0,       # no margin floor
    # Backtest best setting (Nov 14): 4+ wallets, $5K+ each, under 60c.
    "MIN_POSITION_USD": 5_000,       # each wallet must hold at least this much
    "MIN_PRICE": 0.05,               # skip near-dead outcomes
    "MAX_PRICE": 0.60,               # 60c+ was break-even in the backtest
    "MIN_WALLETS_AGREEING": 4,
    "MIN_NET_WALLETS": 3,            # agreeing wallets minus wallets on the other side
    # Freshness filters
    "FRESH_HOURS": 2,                # the Nth wallet must have got in within this window
    "MAX_RUNUP": 0.05,               # skip if price is >5c above their avg entry
    "MAX_DROP": 0.03,                # skip if price is >3c BELOW their avg entry (falling knife)
    "SKIP_STARTED_GAMES": True,      # never alert on a game that has kicked off
    "REALERT_AFTER_HOURS": 12,       # a signal that disappears can't re-alert sooner than this
    "MAX_DAYS_TO_END": 30,           # skip markets ending more than 30 days out
    "MAX_ALERTS_PER_RUN": 10,
    "WALLETS_FILE_MAX_AGE_DAYS": 21, # ignore wallets.json if older than this
}

STATE_FILE = os.environ.get("POLYTAIL_STATE", f"state{SUFFIX}.json")
LOG_FILE = os.environ.get("POLYTAIL_LOG", "signals_log.csv" if not SUFFIX else f"signals{SUFFIX}.csv")
SETTINGS_FILE = os.environ.get("POLYTAIL_SETTINGS", f"settings{SUFFIX}.json")
WALLETS_FILE = os.environ.get("POLYTAIL_WALLETS", f"wallets{SUFFIX}.json")
POOL_FILE = f"wallets{SUFFIX}_pool.json"   # non-bot wallets, written by backtest.py
FILLS_FILE = os.environ.get("POLYTAIL_FILLS", f"fills{SUFFIX}.csv")
BOOKS_FILE = os.environ.get("POLYTAIL_BOOKS", f"books{SUFFIX}.csv")   # sportsbook prices per alert

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
    for period, board in cfg["LEADERBOARDS"]:
        rows = get_json("/v2/leaderboard", {
            "category": cfg["CATEGORY"], "time_period": period.lower(),
            "sort_by": board, "limit": cfg["LEADERBOARD_DEPTH"],
        }) or []
        for row in rows:
            w = (row.get("user_id") or "").lower()
            pnl, vol = num(row.get("pnl")), num(row.get("volume"))
            if not w or pnl < cfg["MIN_PNL"]:
                continue
            if vol > 0 and pnl / vol < cfg["MIN_PNL_TO_VOLUME"]:
                continue
            if w not in wallets or pnl > wallets[w]["pnl"]:
                wallets[w] = {"name": row.get("user_name") or w[:8], "pnl": pnl}
    # Drop the bot / market-maker wallets the backtest excluded, if it has told us which.
    try:
        with open(POOL_FILE) as f:
            pool = json.load(f)
        if (time.time() - num(pool.get("generated_at"))) / 86400 <= cfg["WALLETS_FILE_MAX_AGE_DAYS"]:
            ok = set(pool.get("wallets", []))
            wallets = {w: v for w, v in wallets.items() if w in ok}
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return wallets


# ---------------------------------------------------------------- positions
def open_positions(wallet, cfg):
    rows = get_json("/v2/positions", {
        "user": wallet, "status": "OPEN", "limit": 500,
        "sort_by": "CURRENT_VALUE", "sort_direction": "DESC",
    }) or []
    out, now = [], time.time()
    for p in rows:
        if p.get("redeemable") or int(num(p.get("outcome_index"), 999)) == 999:
            continue
        # No price filter here: the other side of a market has to stay visible so
        # opposing wallets are counted. The price range is applied per signal instead.
        if num(p.get("current_value")) < cfg["MIN_POSITION_USD"]:
            continue
        end = p.get("end_date")
        if end:
            try:
                end_dt = datetime.fromisoformat(end.replace("Z", "+00:00"))
                if end_dt.tzinfo is None:
                    end_dt = end_dt.replace(tzinfo=timezone.utc)
                # end_date is a calendar day; allow the whole day to play out
                if end_dt.timestamp() + 86400 < now:
                    continue
                if end_dt.timestamp() > now + cfg["MAX_DAYS_TO_END"] * 86400:
                    continue
            except ValueError:
                pass
        out.append(p)
    return out


def find_consensus(wallets, positions_by_wallet, cfg):
    groups, now = {}, time.time()
    for w, positions in positions_by_wallet.items():
        sides = {}
        for p in positions:
            sides.setdefault(p.get("condition_id"), set()).add(p.get("outcome_index"))
        for p in positions:
            if len(sides[p.get("condition_id")]) > 1:
                continue  # holds both sides of this market: hedged or market-making, not a view
            key = f"{p.get('condition_id')}|{p.get('outcome_index')}"
            g = groups.setdefault(key, {
                "key": key,
                "title": p.get("title") or "Unknown market",
                "outcome": p.get("outcome") or "?",
                "event_slug": p.get("event_slug") or p.get("slug") or "",
                "condition_id": p.get("condition_id"),
                "outcome_index": p.get("outcome_index"),
                "token_id": p.get("token_id"),
                "price": num(p.get("current_price")),
                "end_date": (p.get("end_date") or "")[:10],
                "holders": [],
            })
            g["holders"].append({
                "wallet": w, "name": wallets[w]["name"], "trader_pnl": wallets[w]["pnl"],
                "value": num(p.get("current_value")), "avg_price": num(p.get("avg_price")),
                "entered": num(p.get("first_entry_at")),
            })

    by_market = {}
    for g in groups.values():
        by_market.setdefault(g["condition_id"], []).append(g)

    signals = []
    for g in groups.values():
        if len(g["holders"]) < cfg["MIN_WALLETS_AGREEING"]:
            continue
        if not (cfg["MIN_PRICE"] <= g["price"] <= cfg["MAX_PRICE"]):
            continue
        g["opposing_wallets"] = sum(len(o["holders"]) for o in by_market[g["condition_id"]]
                                    if o["key"] != g["key"])
        if len(g["holders"]) - g["opposing_wallets"] < cfg["MIN_NET_WALLETS"]:
            continue  # the watched wallets are split on this market
        g["holders"].sort(key=lambda h: h["value"], reverse=True)
        g["total_value"] = sum(h["value"] for h in g["holders"])
        shares = sum(h["value"] / g["price"] for h in g["holders"]) if g["price"] else 0
        cost = sum(h["value"] / g["price"] * h["avg_price"] for h in g["holders"]) if g["price"] else 0
        g["avg_entry"] = cost / shares if shares else 0
        # When did the consensus form? = when the Nth wallet first got in.
        entries = sorted(h["entered"] for h in g["holders"] if h["entered"])
        n = cfg["MIN_WALLETS_AGREEING"]
        g["formed_at"] = entries[n - 1] if len(entries) >= n else 0
        if not g["formed_at"] or now - g["formed_at"] > cfg["FRESH_HOURS"] * 3600:
            continue  # old (or undatable) consensus — the move has likely happened
        if g["price"] - g["avg_entry"] > cfg["MAX_RUNUP"]:
            continue  # price already ran past their entry
        if g["avg_entry"] - g["price"] > cfg["MAX_DROP"]:
            continue  # price has fallen well below their entry — they're losing, don't chase
        signals.append(g)

    if signals and (cfg["SPORTS_GAMES_ONLY"] or cfg["SKIP_STARTED_GAMES"]):
        info = market_info([s["condition_id"] for s in signals])
        if cfg["SPORTS_GAMES_ONLY"]:
            signals = [s for s in signals
                       if info.get(s["condition_id"], {}).get("sport")
                       and (info[s["condition_id"]].get("game_start") or 0) > now]
        else:
            signals = [s for s in signals
                       if not info.get(s["condition_id"], {}).get("game_start")
                       or info[s["condition_id"]]["game_start"] > now]
        for s in signals:
            s["game_start"] = info.get(s["condition_id"], {}).get("game_start")

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
    """Log the alert; returns its timestamp string (the key the fills file joins on)."""
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    new_file = not os.path.exists(LOG_FILE)
    with open(LOG_FILE, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=LOG_FIELDS)
        if new_file:
            w.writeheader()
        w.writerow({
            "alerted_at": stamp,
            "kind": kind, "key": s["key"], "condition_id": s["condition_id"],
            "outcome_index": s["outcome_index"], "outcome": s["outcome"], "title": s["title"],
            "event_slug": s["event_slug"], "price": round(s["price"], 4),
            "avg_entry": round(s["avg_entry"], 4), "wallets": len(s["holders"]),
            "total_value": round(s["total_value"], 2),
            "opposing_wallets": s["opposing_wallets"], "end_date": s["end_date"],
        })
    return stamp


def format_alert(s, is_upgrade):
    head = "📈 MORE TOP TRADERS JOINED" if is_upgrade else "🐋 TOP TRADERS AGREE"
    lines = [
        f"<b>{html.escape(LABEL)}{head}</b>",
        f"<b>{html.escape(s['title'])}</b>",
        f"Side: <b>{html.escape(s['outcome'])}</b> @ {s['price']*100:.0f}¢ now"
        f" (their avg entry {s['avg_entry']*100:.0f}¢)",
        f"{len(s['holders'])} top wallets, {money(s['total_value'])} combined",
    ]
    if s.get("formed_at"):
        mins = max(0, int((time.time() - s["formed_at"]) / 60))
        lines.append(f"Consensus formed {mins // 60}h {mins % 60}m ago")
    if s["opposing_wallets"]:
        lines.append(f"⚠️ {s['opposing_wallets']} top wallet(s) on the other side")
    if s.get("game_start"):
        mins = int((s["game_start"] - time.time()) / 60)
        lines.append(f"Kickoff in {mins // 60}h {mins % 60}m")
    elif s["end_date"]:
        lines.append(f"Ends: {s['end_date']}")
    for q in s.get("books", [])[:2]:   # same bet at the sportsbooks, best price first
        lines.append(f"{html.escape(q['book'])}: {american(q['decimal'])}"
                     f" (like paying {100 / q['decimal']:.0f}¢)")
    lines.append("")
    for h in s["holders"][:6]:
        lines.append(f"• {html.escape(h['name'])} — {money(h['value'])} in"
                     f" (trader P&L {money(h['trader_pnl'])})")
    if len(s["holders"]) > 6:
        lines.append(f"• +{len(s['holders']) - 6} more")
    if s["event_slug"]:
        lines.append(f"\nhttps://polymarket.com/event/{s['event_slug']}")
    return "\n".join(lines)


LABEL = ""


def main():
    global LABEL
    cfg = load_settings()
    LABEL = cfg["LABEL"]
    print(f"Profile: {PROFILE}")
    state = load_state()
    alerted = state.setdefault("alerted", {})
    run_rechecks(state, FILLS_FILE)   # what could you really buy at, a few minutes after each alert?

    wallets = scored_wallets(cfg)
    source = "backtest-scored wallets.json"
    if not wallets:
        wallets, source = leaderboard_wallets(cfg), "leaderboard"
    print(f"Watching {len(wallets)} wallets (from {source})")
    if not wallets:
        print("No wallets returned — API may be down. Exiting without changes.")
        return

    # Check wallets in parallel so a scan finishes in under a minute
    # (GitHub bills each run rounded up to the minute).
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=8) as pool:
        positions = dict(zip(wallets, pool.map(lambda w: open_positions(w, cfg), list(wallets))))

    signals = find_consensus(wallets, positions, cfg)
    print(f"{len(signals)} consensus signals")

    sent, live_keys = 0, set()
    for s in signals:
        live_keys.add(s["key"])
        prev = alerted.get(s["key"])
        if prev:
            prev.pop("gone_at", None)
        is_upgrade = prev is not None and len(s["holders"]) > prev["wallets"]
        if not (prev is None or is_upgrade) or sent >= cfg["MAX_ALERTS_PER_RUN"]:
            continue
        s["books"] = book_quote(s["title"], s["outcome"], s["event_slug"], s.get("game_start"))
        if send_telegram(format_alert(s, is_upgrade)):
            stamp = log_signal(s, "upgrade" if is_upgrade else "new")
            if not is_upgrade:
                log_fill(FILLS_FILE, s["key"], stamp, time.time(), s.get("token_id"), s["price"])
                queue_recheck(state, s["key"], stamp, s.get("token_id"))
                log_books(BOOKS_FILE, s["key"], stamp, s["books"])
            alerted[s["key"]] = {
                "wallets": len(s["holders"]), "title": s["title"], "outcome": s["outcome"],
                "first_seen": (prev or {}).get(
                    "first_seen", datetime.now(timezone.utc).isoformat(timespec="minutes")),
            }
            sent += 1

    # A signal that drops out (price blip, API hiccup) is remembered for a while, so the
    # same bet isn't sent and graded again as a brand-new alert minutes later.
    now = time.time()
    for k in list(alerted):
        if k not in live_keys:
            gone = alerted[k].setdefault("gone_at", now)
            if now - gone > cfg["REALERT_AFTER_HOURS"] * 3600:
                del alerted[k]

    save_state(state)
    print(f"Sent {sent} alert(s)")


if __name__ == "__main__":
    main()
