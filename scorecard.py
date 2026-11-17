"""
PolyTail scorecard — grades every alert the live bot has sent.

For each alert in signals_log.csv, once its market settles, it works out what
$100 bet at the alert price would have returned. Sends a summary to Telegram
and writes results/scorecard.md + results/scorecard.csv.

Alerts are also tracked as separate groups by how many wallets agreed
(3, 4, 5+), each with its own record and progress toward GOAL settled bets.
"""

import csv
import os
from collections import defaultdict
from datetime import datetime, timezone

from common import market_resolutions, money, num, send_telegram, taker_fee

LOG_FILE = os.environ.get("POLYTAIL_LOG", "signals_log.csv")
OUT_DIR = os.environ.get("POLYTAIL_RESULTS", "results")
LABEL = os.environ.get("SCORECARD_LABEL", "PolyTail")
FILE_TAG = os.environ.get("SCORECARD_TAG", "scorecard")
# Only alerts at/after this time count toward the test (rule changes reset it).
SINCE = os.environ.get("SCORECARD_SINCE", "")
STAKE = 100          # pretend bet per alert, $
# Polymarket taker fee rate: fee = stake x rate x (1 - price). Sports 0.03, politics/finance
# 0.04, crypto 0.07 (global site, Fee Structure V2). 0.04 is a slightly cautious default.
FEE_RATE = float(os.environ.get("SCORECARD_FEE_RATE", 0.04))
_stem = os.path.basename(LOG_FILE).replace("signals_log", "fills").replace("signals", "fills")
FILLS_FILE = os.environ.get("POLYTAIL_FILLS", os.path.join(os.path.dirname(LOG_FILE), _stem))
BOOKS_FILE = os.environ.get("POLYTAIL_BOOKS", FILLS_FILE.replace("fills", "books"))
GOAL = 30            # settled bets a group needs before its results mean much

def wallet_group(row):
    n = int(num(row.get("wallets"), 0))
    return "5+" if n >= 5 else str(n)

def load_fills():
    """{(key, alerted_at): {"now": fill price at alert, "later": fill price 2+ min after}}"""
    out = {}
    try:
        with open(FILLS_FILE) as f:
            for r in csv.DictReader(f):
                p = num(r.get("fill_100"), 0)
                if p <= 0 or num(r.get("filled_usd"), 0) < STAKE * 0.99:
                    continue  # no book, or not even $100 for sale
                slot = "now" if num(r.get("secs_after"), 0) < 60 else "later"
                out.setdefault((r["key"], r["alerted_at"]), {}).setdefault(slot, p)
    except FileNotFoundError:
        pass
    return out


def load_books():
    """{(key, alerted_at): (best decimal odds, book name)} from the sportsbook price log."""
    out = {}
    try:
        with open(BOOKS_FILE) as f:
            for r in csv.DictReader(f):
                d, k = num(r.get("decimal"), 0), (r["key"], r["alerted_at"])
                if d > 1 and d > out.get(k, (0, ""))[0]:
                    out[k] = (d, r.get("book", ""))
    except FileNotFoundError:
        pass
    return out


def profit_at(payout, price):
    return round(STAKE * (payout / price - 1) - STAKE * taker_fee(price, FEE_RATE), 2)


def grade(rows):
    res = market_resolutions([r["condition_id"] for r in rows])
    fills, books = load_fills(), load_books()
    graded = []
    for r in rows:
        out = dict(r)
        out["group"] = wallet_group(r)
        price = num(r["price"])
        info = res.get(r["condition_id"])
        idx = int(num(r["outcome_index"], -1))
        q = fills.get((r["key"], r["alerted_at"]), {})
        out["ask_price"], out["later_price"] = q.get("now", ""), q.get("later", "")
        out["profit_ask"] = out["profit_later"] = out["profit_book"] = ""
        dec, out["book"] = books.get((r["key"], r["alerted_at"]), (0, ""))
        out["book_decimal"] = dec or ""
        if info and 0 <= idx < len(info["values"]) and price > 0:
            payout = info["values"][idx]
            out["result"] = "win" if payout >= 0.99 else "loss" if payout <= 0.01 else "void"
            out["profit"] = profit_at(payout, price)
            if q.get("now"):
                out["profit_ask"] = profit_at(payout, q["now"])
            if q.get("later"):
                out["profit_later"] = profit_at(payout, q["later"])
            if dec:   # sportsbook: win pays the odds, loss loses the stake, a push returns it
                out["profit_book"] = round(STAKE * (dec - 1) if payout >= 0.99
                                           else -STAKE if payout <= 0.01 else 0.0, 2)
        else:
            out["result"], out["profit"] = "pending", ""
        graded.append(out)
    return graded

def group_line(items):
    done = [g for g in items if g["result"] != "pending"]
    open_n = len(items) - len(done)
    if not done:
        return f"0/{GOAL} settled, {open_n} open"
    wins = sum(g["result"] == "win" for g in done)
    profit = sum(num(g["profit"]) for g in done)
    breakeven = sum(num(g["price"]) for g in done) / len(done)
    line = (f"{len(done)}/{GOAL} settled, {open_n} open | "
            f"won {wins / len(done):.0%} (break-even ~{breakeven:.0%}) | "
            f"{money(profit)} ({profit / (STAKE * len(done)):+.1%} per bet)")
    if len(done) >= GOAL:
        # 90% range for profit per bet; only call it an edge if the whole range is above zero
        r = [num(g["profit"]) / STAKE for g in done]
        mean = sum(r) / len(r)
        sd = (sum((x - mean) ** 2 for x in r) / (len(r) - 1)) ** 0.5
        low, high = mean - 1.645 * sd / len(r) ** 0.5, mean + 1.645 * sd / len(r) ** 0.5
        rng = f" [90% range {low:+.0%} to {high:+.0%}]"
        if low > 0:
            line += rng + " ✅ edge looks real"
        elif high < 0:
            line += rng + " ❌ losing"
        else:
            line += rng + " ⚠️ could be luck"
    return line

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
    for col, label in [("profit_ask", "the real ask when the alert fired"),
                       ("profit_later", "the real ask a few minutes later (what you'd get)"),
                       ("profit_book", "the best DraftKings/FanDuel price for the same bet")]:
        priced = [g for g in done if g[col] != ""]
        if priced:
            same = sum(num(g["profit"]) for g in priced) / (STAKE * len(priced))
            real = sum(num(g[col]) for g in priced) / (STAKE * len(priced))
            lines.append(f"At {label}: {real:+.1%} per bet over {len(priced)} bets"
                         f" (same bets at the alert's quoted price: {same:+.1%})")
    by_group = defaultdict(list)
    for g in graded:
        by_group[g["group"]].append(g)
    if by_group:
        lines.append(f"\nTracked separately by wallets agreeing (need {GOAL} settled each):")
        for k in sorted(by_group):
            lines.append(f"  {k} wallets: {group_line(by_group[k])}")
    return lines

def main():
    if not os.path.exists(LOG_FILE):
        send_telegram(f"<b>{LABEL} scorecard</b>\nNo alerts logged yet.")
        return
    with open(LOG_FILE) as f:
        rows, seen = [], set()
        for r in csv.DictReader(f):
            # one bet per market side (per rule period, so a rules reset still counts it)
            k = (r["key"], bool(SINCE) and r["alerted_at"] >= SINCE)
            if r.get("kind") == "new" and k not in seen:
                seen.add(k)
                rows.append(r)
    graded = grade(rows)
    current = [g for g in graded if not SINCE or g["alerted_at"] >= SINCE]
    old = [g for g in graded if SINCE and g["alerted_at"] < SINCE]
    lines = summarize(current)
    if SINCE:
        lines.insert(0, f"(Counting alerts since {SINCE[:16].replace('T', ' ')} UTC — current rules)")
    if old:
        done = [g for g in old if g["result"] != "pending"]
        p = sum(num(g["profit"]) for g in done)
        lines.append(f"\nOlder-rule alerts (not counted): {len(done)} settled, "
                     + (f"{p / (STAKE * len(done)):+.1%} per bet" if done else "none settled yet"))

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, f"{FILE_TAG}.csv"), "w", newline="") as f:
        fields = list(graded[0].keys()) + ["counted"] if graded else ["result"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for g in graded:
            w.writerow({**g, "counted": g in current})
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    with open(os.path.join(OUT_DIR, f"{FILE_TAG}.md"), "w") as f:
        f.write(f"# {LABEL} live scorecard ({stamp})\n\n" + "\n".join(lines) + "\n")

    send_telegram(f"<b>📊 {LABEL} weekly scorecard</b>\n" + "\n".join(lines))
    print("\n".join(lines))

if __name__ == "__main__":
    main()
