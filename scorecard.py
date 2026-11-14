"""
PolyTail scorecard — grades every alert the live bot has sent.

For each alert in signals_log.csv, once its market settles, it works out what
$100 bet at the alert price would have returned. Sends a summary to Telegram
and writes results/scorecard.md + results/scorecard.csv.
"""

import csv
import os
from collections import defaultdict
from datetime import datetime, timezone

from common import market_resolutions, money, num, send_telegram

LOG_FILE = os.environ.get("POLYTAIL_LOG", "signals_log.csv")
OUT_DIR = os.environ.get("POLYTAIL_RESULTS", "results")
STAKE = 100          # pretend bet per alert, $
TAKER_FEE = 0.01     # haircut for fees/slippage (1% of stake)


def grade(rows):
    res = market_resolutions([r["condition_id"] for r in rows])
    graded = []
    for r in rows:
        out = dict(r)
        price = num(r["price"])
        info = res.get(r["condition_id"])
        idx = int(num(r["outcome_index"], -1))
        if info and 0 <= idx < len(info["values"]) and price > 0:
            payout = info["values"][idx]
            out["result"] = "win" if payout >= 0.99 else "loss" if payout <= 0.01 else "void"
            out["profit"] = round(STAKE * (payout / price - 1) - STAKE * TAKER_FEE, 2)
        else:
            out["result"], out["profit"] = "pending", ""
        graded.append(out)
    return graded


def summarize(graded):
    done = [g for g in graded if g["result"] != "pending"]
    wins = sum(g["result"] == "win" for g in done)
    profit = sum(num(g["profit"]) for g in done)
    lines = [
        f"Alerts graded: {len(done)} settled, {len(graded) - len(done)} still open",
    ]
    if done:
        lines += [
            f"Win rate: {wins / len(done):.0%}",
            f"Profit if you bet ${STAKE} on each: {money(profit)}"
            f" ({profit / (STAKE * len(done)):+.1%} per bet)",
            f"Avg price paid: {sum(num(g['price']) for g in done) / len(done) * 100:.0f}¢"
            " (break-even win rate ≈ that number)",
        ]
        by_n = defaultdict(list)
        for g in done:
            n = int(num(g["wallets"]))
            by_n["5+" if n >= 5 else str(n)].append(num(g["profit"]))
        lines.append("\nBy number of wallets agreeing:")
        for k in sorted(by_n):
            v = by_n[k]
            lines.append(f"  {k}: {len(v)} bets, {sum(v) / (STAKE * len(v)):+.1%} per bet")
    return lines


def main():
    if not os.path.exists(LOG_FILE):
        send_telegram("<b>PolyTail scorecard</b>\nNo alerts logged yet.")
        return
    with open(LOG_FILE) as f:
        rows = [r for r in csv.DictReader(f) if r.get("kind") == "new"]
    graded = grade(rows)
    lines = summarize(graded)

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "scorecard.csv"), "w", newline="") as f:
        fields = list(graded[0].keys()) if graded else ["result"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(graded)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    with open(os.path.join(OUT_DIR, "scorecard.md"), "w") as f:
        f.write(f"# PolyTail live scorecard ({stamp})\n\n" + "\n".join(lines) + "\n")

    send_telegram("<b>📊 PolyTail weekly scorecard</b>\n" + "\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
