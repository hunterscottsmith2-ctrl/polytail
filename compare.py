"""
PolyTail head-to-head — one Telegram message comparing the four alert tests.

Reads the scorecard CSVs written earlier in the same run (results/<tag>.csv) and lines the
tests up: settled alerts, win rate, return per bet at the alert price, at the real ask a few
minutes later, and at the best sportsbook price. Only names a leader once tests have
enough settled alerts to compare; until then it says so.
"""

import csv
import os
from datetime import datetime, timezone

from common import num, send_telegram

OUT_DIR = os.environ.get("POLYTAIL_RESULTS", "results")
GOAL = 50        # settled alerts a test needs before its record means much
STAKE = 100
TESTS = [  # label, scorecard tag
    ("✅ PROVEN", "scorecard_proven"),
    ("✅🏈 SPORTS PROVEN", "scorecard_sports_proven"),
    ("💰 PROFIT FLOOR", "scorecard"),
    ("💰🏈 SPORTS PROFIT FLOOR", "scorecard_sports"),
]


def load(tag):
    try:
        with open(os.path.join(OUT_DIR, f"{tag}.csv")) as f:
            return [r for r in csv.DictReader(f) if r.get("counted", "True") == "True"]
    except FileNotFoundError:
        return []


def per_bet(rows, col):
    priced = [r for r in rows if r.get(col, "") != ""]
    if not priced:
        return None, 0
    return sum(num(r[col]) for r in priced) / (STAKE * len(priced)), len(priced)


def stats(rows):
    done = [r for r in rows if r.get("result") not in ("pending", "", None)]
    out = {"settled": len(done), "open": len(rows) - len(done)}
    if done:
        out["win"] = sum(r["result"] == "win" for r in done) / len(done)
    for key, col in (("roi", "profit"), ("ask", "profit_later"), ("book", "profit_book")):
        out[key], out[key + "_n"] = per_bet(done, col)
    return out


def fmt(x):
    return "—" if x is None else f"{x:+.1%}"


def main():
    rows, ready = [], []
    for label, tag in TESTS:
        s = stats(load(tag))
        line = f"<b>{label}</b>: {s['settled']}/{GOAL} settled, {s['open']} open"
        if s["settled"]:
            line += (f"\n   won {s['win']:.0%} | alert price {fmt(s['roi'])}/bet"
                     f" | real ask later {fmt(s['ask'])} | sportsbook {fmt(s['book'])}")
        rows.append(line)
        # rank on what you'd really get: the later ask if we have it for most bets, else alert price
        real = s["ask"] if s["ask_n"] >= s["settled"] * 0.5 and s["ask"] is not None else s["roi"]
        if s["settled"] >= GOAL and real is not None:
            ready.append((real, label))
    if len(ready) >= 2:
        ready.sort(reverse=True)
        verdict = f"🏆 Best record so far: {ready[0][1]} ({ready[0][0]:+.1%}/bet at the price you'd get)"
    elif len(ready) == 1:
        verdict = f"Only {ready[0][1]} has {GOAL}+ settled alerts so far — not enough to compare yet"
    else:
        verdict = f"Too early to pick a winner: no test has {GOAL} settled alerts yet"
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    msg = "<b>🏁 PolyTail head-to-head</b>\n" + verdict + "\n\n" + "\n".join(rows)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "head_to_head.md"), "w") as f:
        f.write(f"# PolyTail head-to-head ({stamp})\n\n" + msg.replace("<b>", "**").replace("</b>", "**") + "\n")
    send_telegram(msg)
    print(msg)


if __name__ == "__main__":
    main()
