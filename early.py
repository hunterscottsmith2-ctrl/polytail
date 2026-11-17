"""
PolyTail Early — copy PROVEN sharp wallets the moment they bet, not after a crowd forms.

Watchlist: the "proven" wallets in wallets_sharp.json (made by backtest.py): profitable
on settled markets AND beat the closing price, scored on all data through the backtest
date. NOTE: this exact list has never been tested out of sample. The +3.7%/bet figure
from the Nov 15 backtest (1,706 bets, 90% range -0.4% to +7.9%) was for a different
group (5 wallets picked on training data only); the closest tested group to this list
returned -1.4%/bet over 294 bets. Treat this as an open experiment, not a proven edge.

Every run:
  1. Pull each watched wallet's recent BUY fills.
  2. A wallet putting $1K+ into one side of a market = a signal.
  3. Keep it only if you can still get roughly their price (the order book's ask to buy
     $100 is at most 2 cents above their average entry), the price is 5-95 cents, the market ends
     within 30 days, and (for games) it hasn't kicked off yet.
  4. Log it to signals_early.csv so scorecard.py grades it. Telegram alerts are OFF
     until the test proves itself (set SEND_ALERTS=1 in the workflow to turn them on).

Alert-only: this script never places bets.
"""

import csv
import html
import json
import os
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from common import (GAMMA_API, american, ask_quote, book_quote, log_books, get_pages, get_json, log_fill, money, num, parse_time,
                    queue_recheck, run_rechecks, send_telegram)

WALLETS_FILE = os.environ.get("POLYTAIL_WALLETS", "wallets_sharp.json")
STATE_FILE = "state_early.json"
LOG_FILE = "signals_early.csv"
FILLS_FILE = "fills_early.csv"
BOOKS_FILE = "books_early.csv"
SEND_ALERTS = os.environ.get("SEND_ALERTS", "0") == "1"

MIN_BUY_USD = 1_000        # backtest: $1K setting beat $5K for single sharp wallets
MAX_RUNUP = 0.02           # skip if price already 2c+ above their average entry
MIN_PRICE, MAX_PRICE = 0.05, 0.95
MAX_DAYS_TO_END = 30       # keeps grading fast
LOOKBACK_MIN = 30          # first run / max look-back for new fills
MAX_ALERTS_PER_RUN = 5
FORGET_DAYS = 30

LOG_FIELDS = ["alerted_at", "kind", "key", "condition_id", "outcome_index", "outcome",
              "title", "event_slug", "price", "avg_entry", "wallets", "total_value",
              "opposing_wallets", "end_date", "wallet_names"]

def load_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default

BLOCKLIST_FILE = os.environ.get("POLYTAIL_BLOCKLIST", "wallets_blocklist.json")

def watchlist():
    data = load_json(WALLETS_FILE, {})
    # Wallets cut by hand (survives backtest.py rewriting wallets_sharp.json)
    blocked = {w.lower() for w in load_json(BLOCKLIST_FILE, {}).get("wallets", {})}
    return {w["wallet"].lower(): w for w in data.get("wallets", [])
            if w.get("proven") and w["wallet"].lower() not in blocked}

def recent_buys(wallet, start, end):
    rows, _ = get_pages("/v2/trades", {"user": wallet, "start": int(start), "end": int(end),
                                       "taker_only": "false", "limit": 1000}, max_pages=10)
    return [t for t in rows if t.get("side") == "BUY"
            and int(num(t.get("outcome_index"), 999)) != 999]

def market_snapshot(cids):
    """{cid: {"prices": [...], "end": epoch|None, "start": epoch|None, "closed": bool}}"""
    out, ids = {}, list(dict.fromkeys(c for c in cids if c))
    for i in range(0, len(ids), 25):
        rows = get_json("/markets", {"condition_ids": ids[i:i + 25], "limit": 100},
                        base=GAMMA_API) or []
        for m in rows:
            try:
                prices = [num(p) for p in json.loads(m.get("outcomePrices") or "[]")]
            except (TypeError, json.JSONDecodeError):
                prices = []
            out[m.get("conditionId")] = {
                "prices": prices, "closed": bool(m.get("closed")),
                "end": parse_time(m.get("endDate")),
                "start": parse_time(m.get("gameStartTime")),
            }
        time.sleep(0.1)
    return out

def main():
    now = time.time()
    state = load_json(STATE_FILE, {"seen": {}, "last_run": 0})
    seen = state.setdefault("seen", {})
    run_rechecks(state, FILLS_FILE)   # price a few minutes after earlier signals
    start = max(state.get("last_run", 0) - 300, now - LOOKBACK_MIN * 60)

    wallets = watchlist()
    print(f"Watching {len(wallets)} proven sharp wallets; fills since "
          f"{datetime.fromtimestamp(start, timezone.utc):%H:%M} UTC")
    if not wallets:
        print("No proven wallets in wallets_sharp.json — run the backtest first.")
        return

    with ThreadPoolExecutor(max_workers=8) as pool:
        fills = dict(zip(wallets, pool.map(lambda w: recent_buys(w, start, now), list(wallets))))

    # wallet + market side -> cost / shares in this window
    agg = defaultdict(lambda: {"cost": 0.0, "shares": 0.0})
    meta = {}
    for w, rows in fills.items():
        for t in rows:
            key = f"{t['condition_id']}|{int(num(t['outcome_index']))}"
            a = agg[(w, key)]
            a["cost"] += num(t["size"]) * num(t["price"])
            a["shares"] += num(t["size"])
            meta[key] = t
    cands = {(w, k): a for (w, k), a in agg.items()
             if a["cost"] >= MIN_BUY_USD and f"{w}|{k}" not in seen}
    snap = market_snapshot([k.split("|")[0] for _, k in cands])

    signals = {}
    for (w, key), a in cands.items():
        cid, idx = key.split("|")[0], int(key.split("|")[1])
        m, t = snap.get(cid), meta[key]
        avg = a["cost"] / a["shares"] if a["shares"] else 0
        reason = None
        if not m or m["closed"] or idx >= len(m["prices"]):
            reason = "closed/unknown"
        else:
            # Real cost to buy $100 now; the Gamma price can lag and is not the ask.
            q = ask_quote(t.get("token_id"))
            price = q["fill"] if q else m["prices"][idx]
            if not (MIN_PRICE <= price <= MAX_PRICE):
                reason = "price out of range"
            elif price - avg > MAX_RUNUP:
                reason = "price already moved"
            elif m["end"] and m["end"] > now + MAX_DAYS_TO_END * 86400:
                reason = "ends too far out"
            elif m["start"] and m["start"] <= now:
                reason = "game already started"
        seen[f"{w}|{key}"] = now  # never re-evaluate the same wallet + side
        if reason:
            continue
        s = signals.setdefault(key, {
            "key": key, "condition_id": cid, "outcome_index": idx,
            "outcome": t.get("outcome") or "?", "title": t.get("title") or "?",
            "event_slug": t.get("event_slug") or "", "price": price,
            "token_id": t.get("token_id"),
            "end_date": datetime.fromtimestamp(m["end"], timezone.utc).strftime("%Y-%m-%d")
            if m["end"] else "", "holders": [], "game_start": m["start"]})
        s["holders"].append({"name": wallets[w].get("name", w[:8])[:24], "cost": a["cost"],
                             "avg": avg, "clv": wallets[w].get("clv_avg_cents")})

    new_file = not os.path.exists(LOG_FILE)
    sent = 0
    with open(LOG_FILE, "a", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=LOG_FIELDS)
        if new_file:
            wr.writeheader()
        for s in sorted(signals.values(), key=lambda s: -sum(h["cost"] for h in s["holders"])):
            cost = sum(h["cost"] for h in s["holders"])
            avg = sum(h["avg"] * h["cost"] for h in s["holders"]) / cost
            stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
            log_fill(FILLS_FILE, s["key"], stamp, time.time(), s["token_id"], s["price"])
            queue_recheck(state, s["key"], stamp, s["token_id"])
            books = book_quote(s["title"], s["outcome"], s["event_slug"], s["game_start"])
            log_books(BOOKS_FILE, s["key"], stamp, books)
            wr.writerow({
                "alerted_at": stamp,
                "kind": "new", "key": s["key"], "condition_id": s["condition_id"],
                "outcome_index": s["outcome_index"], "outcome": s["outcome"], "title": s["title"],
                "event_slug": s["event_slug"], "price": round(s["price"], 4),
                "avg_entry": round(avg, 4), "wallets": len(s["holders"]),
                "total_value": round(cost, 2), "opposing_wallets": 0, "end_date": s["end_date"],
                "wallet_names": "; ".join(h["name"] for h in s["holders"]),
            })
            if SEND_ALERTS and sent < MAX_ALERTS_PER_RUN:
                lines = ["<b>🎯 SHARP WALLET JUST BET</b>", f"<b>{html.escape(s['title'])}</b>",
                         f"Side: <b>{html.escape(s['outcome'])}</b> @ {s['price']*100:.0f}¢ now "
                         f"(they paid {avg*100:.0f}¢)"]
                for h in s["holders"]:
                    lines.append(f"• {html.escape(h['name'])} — {money(h['cost'])} "
                                 f"(beats the close by {h['clv']}¢ on avg)")
                for q in books[:2]:
                    lines.append(f"{html.escape(q['book'])}: {american(q['decimal'])}"
                                 f" (like paying {100 / q['decimal']:.0f}¢)")
                if s["game_start"]:
                    mins = int((s["game_start"] - now) / 60)
                    lines.append(f"Starts in {mins // 60}h {mins % 60}m")
                if s["event_slug"]:
                    lines.append(f"\nhttps://polymarket.com/event/{s['event_slug']}")
                send_telegram("\n".join(lines))
                sent += 1

    state["seen"] = {k: v for k, v in seen.items() if now - v < FORGET_DAYS * 86400}
    state["last_run"] = now
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=0, sort_keys=True)
    print(f"{len(cands)} new $1K+ entries, {len(signals)} logged signals, {sent} alerts sent")

if __name__ == "__main__":
    main()
