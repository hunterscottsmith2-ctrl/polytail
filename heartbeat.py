"""
PolyTail daily check-in — one Telegram message saying whether every test is alive.

For each test: when it last scanned, how many wallets it watched, alerts in the last
24 hours. Also how old the wallet lists are (they go stale after 21 days) and whether
sportsbook prices are being recorded. Problems are marked ⚠️ at the top.
"""

import csv
import json
import os
import time
from datetime import datetime, timezone

from common import send_telegram

STALE_SCAN_MIN = 20       # the live loop scans every 3 min; 20+ min quiet means it's down
LIST_WARN_DAYS = 14       # lists stop being used at 21 days
LIST_MAX_DAYS = 21

TESTS = [  # label, scan status file, signals log
    ("✅ PROVEN", "scan_status_proven.json", "signals_proven.csv"),
    ("✅🏈 SPORTS PROVEN", "scan_status_sports_proven.json", "signals_sports_proven.csv"),
    ("💰 PROFIT FLOOR", "scan_status.json", "signals_log.csv"),
    ("💰🏈 SPORTS PROFIT FLOOR", "scan_status_sports.json", "signals_sports.csv"),
    ("🎯 EARLY (silent)", None, "signals_early.csv"),
]
LISTS = [  # label, file
    ("✅ PROVEN list", "wallets_proven.json"),
    ("✅🏈 SPORTS PROVEN list", "wallets_sports_proven.json"),
    ("💰 PROFIT FLOOR bot filter", "wallets_pool.json"),
    ("💰🏈 SPORTS PROFIT FLOOR bot filter", "wallets_sports_pool.json"),
]


def ts(s):
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
    except (AttributeError, ValueError):
        return None


def alerts_last_day(path, now):
    try:
        with open(path) as f:
            return sum(r.get("kind", "new") == "new" and (ts(r.get("alerted_at", "")) or 0) >= now - 86400
                       for r in csv.DictReader(f))
    except FileNotFoundError:
        return 0


def main():
    now = time.time()
    problems, lines = [], []
    for label, status_file, log_file in TESTS:
        n = alerts_last_day(log_file, now)
        if status_file is None:
            lines.append(f"{label}: {n} logged in 24h")
            continue
        try:
            with open(status_file) as f:
                st = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            st = {}
        at = ts(st.get("at", ""))
        mins = (now - at) / 60 if at else None
        watched = st.get("wallets_watched", 0)
        if mins is None or mins > STALE_SCAN_MIN:
            when = "never" if mins is None else f"{mins / 60:.1f}h ago"
            problems.append(f"⚠️ {label} hasn't scanned since {when}")
        elif not watched:
            problems.append(f"⚠️ {label} is watching 0 wallets")
        ago = "—" if mins is None else f"{mins:.0f}m ago"
        lines.append(f"{label}: {watched} wallets, {n} alert(s) in 24h, last scan {ago}")

    lines.append("")
    for label, path in LISTS:
        try:
            with open(path) as f:
                d = json.load(f)
            age = (now - float(d.get("generated_at") or 0)) / 86400
            count = len(d.get("wallets", []))
        except (FileNotFoundError, json.JSONDecodeError, ValueError):
            problems.append(f"⚠️ {label} is missing")
            continue
        if age > LIST_MAX_DAYS:
            problems.append(f"⚠️ {label} is {age:.0f} days old and no longer used — run the backtest")
        elif age > LIST_WARN_DAYS:
            problems.append(f"⚠️ {label} is {age:.0f} days old (stops at {LIST_MAX_DAYS}) — Saturday's backtest should refresh it")
        lines.append(f"{label}: {count} wallets, {age:.0f} days old")

    books = bool(os.environ.get("ODDS_API_KEY"))
    lines.append("\nSportsbook prices (DraftKings/FanDuel): " + ("ON" if books else "OFF — add an ODDS_API_KEY secret"))

    head = "✅ All tests running" if not problems else "\n".join(problems)
    msg = "<b>🩺 PolyTail daily check-in</b>\n" + head + "\n\n" + "\n".join(lines)
    send_telegram(msg)
    print(msg)


if __name__ == "__main__":
    main()
