"""
PolyTail backfill — find the alerts the live bot missed during an outage.

Replays the watched wallets' real trades over a time window, using the same consensus
rule as the live bot (and the backtest), and writes every alert that would have fired to
signals_backfill.csv / signals_backfill_sports.csv. scorecard.py grades those separately
from real alerts, so a gap in the live bot doesn't leave a hole in the paper record.

Usage (set POLYTAIL_PROFILE=sports for the sports test):
  BACKFILL_START=2026-11-19T16:25:00Z BACKFILL_END=2026-11-20T20:25:00Z python backfill.py

Limits: entry price is the 3rd wallet's fill +1¢ (the live bot alerts within ~3 minutes,
so this is close but not exact), and the price run-up / drop checks aren't applied.
"""

import csv
import os
import sys
import time
from datetime import datetime, timezone

import tracker                      # same settings, wallet lists and log format as the live bot
import backtest                     # same trade download + replay as the backtest
from common import GAMMA_API, _sport_fields, get_json, parse_time

PROFILE = tracker.PROFILE
OUT_FILE = "signals_backfill.csv" if PROFILE == "main" else f"signals_backfill_{PROFILE}.csv"
HISTORY_DAYS = 45                   # trades before the window, so existing positions count


def iso(ts):
    return datetime.fromtimestamp(ts, timezone.utc).isoformat(timespec="seconds")


def market_details(cids):
    """{cid: {"sport", "game_start", "end"}} for open and closed markets."""
    out, ids = {}, list(dict.fromkeys(cids))
    for i in range(0, len(ids), 25):
        for closed in ("true", "false"):
            for m in get_json("/markets", {"condition_ids": ids[i:i + 25], "closed": closed,
                                           "limit": 100}, base=GAMMA_API) or []:
                if m.get("conditionId"):
                    out[m["conditionId"]] = {**_sport_fields(m), "end": parse_time(m.get("endDate"))}
        time.sleep(0.1)
    return out


def main():
    start = parse_time(os.environ["BACKFILL_START"])
    end = parse_time(os.environ["BACKFILL_END"])
    now = time.time()
    cfg = tracker.load_settings()
    wallets = tracker.scored_wallets(cfg) or tracker.leaderboard_wallets(cfg)
    print(f"Profile {PROFILE}: {len(wallets)} wallets, window {iso(start)} → {iso(end)}")
    if not wallets:
        sys.exit("No wallets — API may be down.")

    trades, skipped = [], 0
    for i, w in enumerate(wallets, 1):
        tr = backtest.wallet_trades(w, start - HISTORY_DAYS * 86400, end, now)
        if tr is None:
            skipped += 1
        else:
            trades.extend(tr)
        if i % 20 == 0:
            print(f"  trades for {i}/{len(wallets)} wallets")
    trades.sort(key=lambda t: t["ts"])
    print(f"{len(trades)} trades ({skipped} wallets skipped: too many trades or download failed)")

    n = cfg["MIN_WALLETS_AGREEING"]
    signals = [s for s in backtest.replay(trades, set(wallets), n, cfg["MIN_POSITION_USD"], start)
               if s["ts"] < end]
    print(f"{len(signals)} raw consensus moments in the window")

    # Already alerted live? Then it isn't missed.
    live = set()
    try:
        with open(tracker.LOG_FILE) as f:
            live = {r["key"] for r in csv.DictReader(f) if start <= parse_time(r["alerted_at"]) < end}
    except FileNotFoundError:
        pass

    info = market_details(s["cid"] for s in signals)
    kept, why = [], {}
    for s in signals:
        price = min(s["trigger_price"] + 0.01, 0.99)
        m = info.get(s["cid"], {})
        reason = None
        if f"{s['cid']}|{s['idx']}" in live:
            reason = "alerted live"
        elif not (cfg["MIN_PRICE"] <= price <= cfg["MAX_PRICE"]):
            reason = "price out of range"
        elif s["wallets"] - s["opposing"] < cfg["MIN_NET_WALLETS"]:
            reason = "watched wallets split"
        elif m.get("end") and m["end"] > s["ts"] + cfg["MAX_DAYS_TO_END"] * 86400:
            reason = "ends too far out"
        elif cfg["SKIP_STARTED_GAMES"] and m.get("game_start") and m["game_start"] <= s["ts"]:
            reason = "game already started"
        elif cfg["SPORTS_GAMES_ONLY"] and not m.get("sport"):
            reason = "not a sports game"
        if reason:
            why[reason] = why.get(reason, 0) + 1
            continue
        kept.append((s, price, m))
    print("Filtered out:", why or "none")
    print(f"{len(kept)} missed alert(s)")

    # Replace this window's rows (re-running is safe), keep anything else already backfilled.
    rows = []
    try:
        with open(OUT_FILE) as f:
            rows = [r for r in csv.DictReader(f) if not start <= parse_time(r["alerted_at"]) < end]
    except FileNotFoundError:
        pass
    for s, price, m in kept:
        rows.append({
            "alerted_at": iso(s["ts"]), "kind": "new", "key": f"{s['cid']}|{s['idx']}",
            "condition_id": s["cid"], "outcome_index": s["idx"], "outcome": s["outcome"],
            "title": s["title"], "event_slug": s["slug"], "price": round(price, 4),
            "avg_entry": round(s["trigger_price"], 4), "wallets": s["wallets"], "total_value": "",
            "opposing_wallets": s["opposing"],
            "end_date": datetime.fromtimestamp(m["end"], timezone.utc).strftime("%Y-%m-%d") if m.get("end") else "",
        })
        print(f"  {iso(s['ts'])[:16]}  {s['title'][:60]} — {s['outcome']} @ {price:.0%}")
    rows.sort(key=lambda r: r["alerted_at"])
    with open(OUT_FILE, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=tracker.LOG_FIELDS)
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
