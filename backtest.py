"""
PolyTail backtest — would tailing top-trader consensus actually have made money?

Walk-forward design, so the test can't cheat by knowing the future:
  * TRAIN window (e.g. 240 -> 90 days ago): score every wallet using ONLY markets
    that had settled before the cutoff. Pick the ones with a real track record.
  * TEST window (last 90 days): replay those wallets' actual trades in time order.
    Each time N of them end up holding the same side of a market, that's a signal.
    We "bet" at the market price 15 minutes later (alert delay), pay a 1% fee
    haircut, and grade the bet when the market settled.

It also runs the same test on the whole wallet pool (no scoring) so you can see
whether picking wallets carefully adds anything, and on N=1 (tail every single
entry) as a baseline.

Outputs (in results/):
  backtest_report.md   - plain-English summary + table of every setting tried
  backtest_signals.csv - every simulated bet
  wallet_scores.csv    - how each wallet scored in the training window
  recommended_settings.json - only if an edge was found
and wallets.json (live watchlist for tracker.py) only if scoring beat the pool.
A short summary is sent to Telegram.
"""

import csv
import json
import math
import os
import random
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone

from common import get_json, market_resolutions, money, num, send_telegram

# ---------------------------------------------------------------- settings
LOOKBACK_DAYS = int(os.environ.get("BT_LOOKBACK_DAYS", 240))
TEST_DAYS = int(os.environ.get("BT_TEST_DAYS", 90))
POOL_DEPTH = int(os.environ.get("BT_POOL_DEPTH", 100))   # per leaderboard
POOL_BOARDS = [("ALL", "PNL"), ("MONTH", "PNL"), ("ALL", "VOL"), ("MONTH", "VOL")]

MAX_TRADES_PER_WALLET = 30_000   # more than this = bot / market maker, skip
MIN_TRAIN_MARKETS = 15           # wallet needs this many settled markets in training
MIN_TRAIN_ROI = 0.05             # ...and at least +5% return on money bet
MIN_TRAIN_PNL = 5_000            # ...and at least $5K profit

N_GRID = [1, 2, 3, 4, 5]         # wallets that must agree
MIN_POS_GRID = [1_000, 5_000]    # $ each wallet must have in the position
MIN_PRICE, MAX_PRICE = 0.05, 0.95
DELAY_MINUTES = 15               # you see the alert & bet this long after
SLIPPAGE = 0.01                  # used if no price history is available
TAKER_FEE = 0.01                 # 1% haircut on each bet
MAX_PRICE_LOOKUPS = 4_000
MIN_SIGNALS_FOR_VERDICT = 30

CLOB_API = "https://clob.polymarket.com"
CACHE_DIR = os.environ.get("BT_CACHE", "cache")
OUT_DIR = os.environ.get("POLYTAIL_RESULTS", "results")
WALLETS_FILE = os.environ.get("POLYTAIL_WALLETS", "wallets.json")
DAY = 86400
WINDOW = 30 * DAY


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


# ---------------------------------------------------------------- cache
def cache_get(name):
    try:
        with open(os.path.join(CACHE_DIR, name)) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def cache_put(name, obj):
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(os.path.join(CACHE_DIR, name), "w") as f:
        json.dump(obj, f)


# ---------------------------------------------------------------- data pulls
def wallet_pool():
    pool = {}
    for period, order in POOL_BOARDS:
        for offset in range(0, POOL_DEPTH, 50):
            rows = get_json("/v1/leaderboard", {"category": "OVERALL", "timePeriod": period,
                                                "orderBy": order, "limit": 50,
                                                "offset": offset}) or []
            for r in rows:
                w = (r.get("proxyWallet") or "").lower()
                if w:
                    pool.setdefault(w, {"name": r.get("userName") or w[:8]})
            if len(rows) < 50:
                break
    return pool


def wallet_trades(wallet, start, end, now):
    """All of a wallet's fills (maker + taker) between start and end, oldest first."""
    trades, seen = [], set()
    win_start = (start // WINDOW) * WINDOW
    while win_start < end:
        win_end = win_start + WINDOW
        name = f"trades_{wallet}_{int(win_start)}.json"
        rows = cache_get(name) if win_end < now - DAY else None
        if rows is None:
            rows = []
            for offset in range(0, 10_001, 5_000):
                page = get_json("/trades", {"user": wallet, "start": int(win_start),
                                            "end": int(win_end), "limit": 5_000,
                                            "offset": offset, "takerOnly": "false"}) or []
                rows.extend(page)
                if len(page) < 5_000:
                    break
                if offset == 10_000:
                    return None  # >15K fills in a month: bot / market maker
                time.sleep(0.1)
            if win_end < now - DAY:
                cache_put(name, rows)
        for t in rows:
            k = (t.get("transactionHash"), t.get("asset"), t.get("side"),
                 t.get("size"), t.get("price"), t.get("timestamp"))
            if k in seen:
                continue
            seen.add(k)
            ts = num(t.get("timestamp"))
            if start <= ts < end:
                trades.append({
                    "wallet": wallet, "ts": ts, "side": t.get("side"),
                    "cid": t.get("conditionId"), "idx": int(num(t.get("outcomeIndex"), -1)),
                    "asset": t.get("asset"), "size": num(t.get("size")),
                    "price": num(t.get("price")), "title": t.get("title") or "",
                    "outcome": t.get("outcome") or "", "slug": t.get("eventSlug") or "",
                })
        if len(trades) > MAX_TRADES_PER_WALLET:
            return None
        win_start = win_end
        time.sleep(0.1)
    trades.sort(key=lambda t: t["ts"])
    return trades


def price_after(asset, ts, lookups):
    """Market price DELAY_MINUTES after ts, from Polymarket's price history."""
    key = f"{asset}_{int(ts // 300)}"
    if key in lookups["cache"]:
        return lookups["cache"][key]
    if lookups["count"] >= MAX_PRICE_LOOKUPS:
        return None
    lookups["count"] += 1
    target = ts + DELAY_MINUTES * 60
    body = get_json("/prices-history", {"market": asset, "startTs": int(target),
                                        "endTs": int(target + 6 * 3600), "fidelity": 1},
                    base=CLOB_API)
    hist = body.get("history", []) if isinstance(body, dict) else []
    p = num(hist[0].get("p"), None) if hist else None
    lookups["cache"][key] = p
    return p


# ---------------------------------------------------------------- scoring
def market_pnl(trades, res, as_of):
    """Per-market profit for one wallet, counting only markets settled before as_of."""
    per = defaultdict(lambda: {"cash": 0.0, "cost": 0.0, "shares": defaultdict(float)})
    for t in trades:
        if t["ts"] >= as_of or t["idx"] < 0:
            continue
        m = per[t["cid"]]
        amt = t["size"] * t["price"]
        if t["side"] == "BUY":
            m["cash"] -= amt
            m["cost"] += amt
            m["shares"][t["idx"]] += t["size"]
        else:
            m["cash"] += amt
            m["shares"][t["idx"]] -= t["size"]
    out = {}
    for cid, m in per.items():
        info = res.get(cid)
        if not info or not info["resolved_at"] or info["resolved_at"] >= as_of:
            continue
        if any(s < -1 for s in m["shares"].values()) or m["cost"] <= 0:
            continue  # history incomplete (bought before window / via split)
        value = sum(max(s, 0) * (info["values"][i] if i < len(info["values"]) else 0)
                    for i, s in m["shares"].items())
        out[cid] = {"pnl": m["cash"] + value, "cost": m["cost"],
                    "month": int(info["resolved_at"] // WINDOW)}
    return out


def score_wallet(trades, res, as_of):
    mk = market_pnl(trades, res, as_of)
    cost = sum(m["cost"] for m in mk.values())
    pnl = sum(m["pnl"] for m in mk.values())
    months = defaultdict(float)
    for m in mk.values():
        months[m["month"]] += m["pnl"]
    return {
        "markets": len(mk), "cost": cost, "pnl": pnl,
        "roi": pnl / cost if cost else 0.0,
        "market_win_rate": (sum(m["pnl"] > 0 for m in mk.values()) / len(mk)) if mk else 0.0,
        "months_positive": f"{sum(v > 0 for v in months.values())}/{len(months)}",
    }


def passes(s):
    return (s["markets"] >= MIN_TRAIN_MARKETS and s["roi"] >= MIN_TRAIN_ROI
            and s["pnl"] >= MIN_TRAIN_PNL)


# ---------------------------------------------------------------- replay
def replay(all_trades, wallet_set, n_needed, min_pos, cutoff):
    """Walk trades in time order; emit a signal when n_needed wallets hold the same side."""
    # cid -> outcome idx -> wallet -> [shares, cost]
    hold = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [0.0, 0.0])))
    fired, signals = set(), []
    for t in all_trades:
        if t["wallet"] not in wallet_set or t["idx"] < 0:
            continue
        key = (t["cid"], t["idx"])
        pos = hold[t["cid"]][t["idx"]][t["wallet"]]
        if t["side"] == "BUY":
            pos[0] += t["size"]
            pos[1] += t["size"] * t["price"]
        else:
            if pos[0] > 0:
                frac = min(t["size"] / pos[0], 1.0)
                pos[1] *= (1 - frac)
            pos[0] = max(pos[0] - t["size"], 0.0)
        if t["ts"] < cutoff or key in fired or t["side"] != "BUY":
            continue
        holders = [w for w, p in hold[t["cid"]][t["idx"]].items() if p[0] > 0 and p[1] >= min_pos]
        if len(holders) >= n_needed:
            fired.add(key)
            opposing = sum(1 for idx, ws in hold[t["cid"]].items() if idx != t["idx"]
                           for p in ws.values() if p[0] > 0 and p[1] >= min_pos)
            signals.append({"ts": t["ts"], "cid": t["cid"], "idx": t["idx"],
                            "asset": t["asset"], "trigger_price": t["price"],
                            "title": t["title"], "outcome": t["outcome"], "slug": t["slug"],
                            "wallets": len(holders), "opposing": opposing})
    return signals


def bootstrap_ci(xs, reps=2000, seed=7):
    if len(xs) < 5:
        return (float("nan"), float("nan"))
    rng = random.Random(seed)
    means = sorted(sum(rng.choice(xs) for _ in xs) / len(xs) for _ in range(reps))
    return means[int(0.05 * reps)], means[int(0.95 * reps)]


def evaluate(signals, res, lookups):
    rows = []
    for s in signals:
        info = res.get(s["cid"])
        delayed = price_after(s["asset"], s["ts"], lookups) if s["asset"] else None
        entry = delayed if delayed else min(s["trigger_price"] + SLIPPAGE, 0.99)
        row = dict(s, entry=round(entry, 4), price_source="history" if delayed else "trigger+1¢")
        if not (MIN_PRICE <= entry <= MAX_PRICE):
            row["status"] = "skipped (price out of range)"
        elif not info or s["idx"] >= len(info["values"]):
            row["status"] = "pending"
        else:
            payout = info["values"][s["idx"]]
            row.update(status="settled", payout=payout,
                       roi=round(payout / entry - 1 - TAKER_FEE, 4))
        rows.append(row)
    return rows


def stats(rows):
    done = [r for r in rows if r.get("status") == "settled"]
    rois = [r["roi"] for r in done]
    lo, hi = bootstrap_ci(rois)
    return {
        "signals": len(rows), "settled": len(done),
        "win_rate": sum(r["payout"] >= 0.99 for r in done) / len(done) if done else 0,
        "avg_entry": sum(r["entry"] for r in done) / len(done) if done else 0,
        "mean_roi": sum(rois) / len(rois) if rois else 0,
        "median_roi": sorted(rois)[len(rois) // 2] if rois else 0,
        "ci_low": lo, "ci_high": hi,
        "profit_100": sum(100 * x for x in rois),
    }


# ---------------------------------------------------------------- main
def pct(x):
    return "n/a" if x != x else f"{x:+.1%}"  # x != x catches NaN


def main():
    now = time.time()
    start, cutoff = now - LOOKBACK_DAYS * DAY, now - TEST_DAYS * DAY
    log(f"Train: {datetime.fromtimestamp(start, timezone.utc):%Y-%m-%d} → "
        f"{datetime.fromtimestamp(cutoff, timezone.utc):%Y-%m-%d}, test → today")

    pool = wallet_pool()
    log(f"Wallet pool: {len(pool)}")
    if not pool:
        send_telegram("PolyTail backtest: couldn't load the leaderboard. Try again later.")
        sys.exit(1)

    trades_by_wallet, bots = {}, 0
    for i, w in enumerate(pool, 1):
        tr = wallet_trades(w, start, now, now)
        if tr is None:
            bots += 1
        elif tr:
            trades_by_wallet[w] = tr
        if i % 25 == 0:
            log(f"  trades pulled for {i}/{len(pool)} wallets")
    log(f"Usable wallets: {len(trades_by_wallet)} (skipped {bots} bot-like)")

    res_cache = cache_get("resolutions.json") or {}
    all_cids = {t["cid"] for tr in trades_by_wallet.values() for t in tr}
    log(f"Looking up results for {len(all_cids)} markets")
    res = market_resolutions(list(all_cids), cache=res_cache)
    cache_put("resolutions.json", {k: v for k, v in res_cache.items() if v})
    log(f"{len(res)} markets settled")

    # Score wallets on training data only.
    scores = {w: score_wallet(tr, res, cutoff) for w, tr in trades_by_wallet.items()}
    selected = {w for w, s in scores.items() if passes(s)}
    log(f"Selected {len(selected)} wallets from training window")

    all_trades = sorted((t for tr in trades_by_wallet.values() for t in tr), key=lambda t: t["ts"])
    lookups = {"cache": cache_get("prices.json") or {}, "count": 0}

    sets = {"scored": selected, "whole pool": set(trades_by_wallet)}
    table, sig_rows = [], []
    for set_name, wset in sets.items():
        for n in N_GRID:
            for mp in MIN_POS_GRID:
                sigs = replay(all_trades, wset, n, mp, cutoff)
                rows = evaluate(sigs, res, lookups)
                st = stats(rows)
                table.append({"wallets": set_name, "N": n, "min_pos": mp, **st})
                for r in rows:
                    sig_rows.append({"wallet_set": set_name, "N": n, "min_pos": mp, **r})
                log(f"  {set_name:10} N={n} min ${mp:>5}: {st['settled']:4} settled, "
                    f"mean {pct(st['mean_roi'])}")
    cache_put("prices.json", lookups["cache"])

    # ---------- verdict
    def ok(r):
        return r["N"] >= 2 and r["settled"] >= MIN_SIGNALS_FOR_VERDICT

    candidates = [r for r in table if ok(r) and r["ci_low"] == r["ci_low"] and r["ci_low"] > 0]
    best = max(candidates, key=lambda r: r["mean_roi"]) if candidates else None
    scored_main = next((r for r in table if r["wallets"] == "scored" and r["N"] == 3
                        and r["min_pos"] == 1_000), None)
    pool_main = next((r for r in table if r["wallets"] == "whole pool" and r["N"] == 3
                      and r["min_pos"] == 1_000), None)
    scoring_helps = bool(scored_main and pool_main and scored_main["settled"] >= 10
                         and scored_main["mean_roi"] > pool_main["mean_roi"])

    if best:
        verdict = (f"✅ Edge found: {best['wallets']} wallets, N={best['N']}, min ${best['min_pos']:,}"
                   f" → {pct(best['mean_roi'])} per bet over {best['settled']} settled bets"
                   f" (90% range {pct(best['ci_low'])} to {pct(best['ci_high'])}).")
    else:
        verdict = ("❌ No setting showed a reliable edge (needs 30+ settled bets with the whole"
                   " 90% range above zero). Don't bet real money on these alerts yet.")

    # ---------- outputs
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "backtest_signals.csv"), "w", newline="") as f:
        fields = sorted({k for r in sig_rows for k in r}) if sig_rows else ["none"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(sig_rows)
    with open(os.path.join(OUT_DIR, "wallet_scores.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["wallet", "name", "selected", "markets", "cost", "pnl", "roi",
                    "market_win_rate", "months_positive"])
        for wal, s in sorted(scores.items(), key=lambda kv: -kv[1]["pnl"]):
            w.writerow([wal, pool[wal]["name"], wal in selected, s["markets"], round(s["cost"]),
                        round(s["pnl"]), round(s["roi"], 4), round(s["market_win_rate"], 3),
                        s["months_positive"]])

    lines = [
        "# PolyTail backtest report",
        f"Run {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC. Training window "
        f"{LOOKBACK_DAYS - TEST_DAYS} days, test window {TEST_DAYS} days.",
        f"Wallet pool {len(pool)}, usable {len(trades_by_wallet)}, bot-like skipped {bots}, "
        f"selected by training score {len(selected)}.",
        "",
        f"**Verdict:** {verdict}",
        "",
        f"Bets placed at the price {DELAY_MINUTES} min after the signal, minus a "
        f"{TAKER_FEE:.0%} fee. A random bet at market price averages about -1% "
        "after that fee, so that's the bar to beat.",
        f"Scoring wallets {'beat' if scoring_helps else 'did NOT beat'} using the whole "
        "pool (N=3, $1K).",
        "",
        "| Wallets | N | Min $ | Signals | Settled | Win rate | Avg price | Mean ROI | 90% range | $100/bet total |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in table:
        lines.append(f"| {r['wallets']} | {r['N']} | {r['min_pos']:,} | {r['signals']} | "
                     f"{r['settled']} | {r['win_rate']:.0%} | {r['avg_entry']*100:.0f}¢ | "
                     f"{pct(r['mean_roi'])} | {pct(r['ci_low'])} to {pct(r['ci_high'])} | "
                     f"{money(r['profit_100'])} |")
    if best:
        b = [r for r in sig_rows if r["wallet_set"] == best["wallets"] and r["N"] == best["N"]
             and r["min_pos"] == best["min_pos"] and r.get("status") == "settled"]
        lines += ["", "## Best setting by entry price", "| Price | Bets | Mean ROI |", "|---|---|---|"]
        for lo, hi, label in [(0, .3, "under 30¢"), (.3, .6, "30–60¢"), (.6, 1, "60¢+")]:
            xs = [r["roi"] for r in b if lo <= r["entry"] < hi]
            if xs:
                lines.append(f"| {label} | {len(xs)} | {pct(sum(xs)/len(xs))} |")
        with open(os.path.join(OUT_DIR, "recommended_settings.json"), "w") as f:
            json.dump({"MIN_WALLETS_AGREEING": best["N"], "MIN_POSITION_USD": best["min_pos"]},
                      f, indent=1)
    lines += ["", "## Caveats",
              "- The wallet pool comes from today's leaderboards, which partly reflect test-window "
              "profits. The volume boards and training-only scoring reduce this, but results may "
              "still be a bit optimistic.",
              f"- {lookups['count']} prices pulled from history; others use trigger price +1¢.",
              "- Past results don't guarantee future ones. Markets adapt when edges get crowded."]
    report = "\n".join(lines) + "\n"
    with open(os.path.join(OUT_DIR, "backtest_report.md"), "w") as f:
        f.write(report)

    # Live watchlist: re-score on all settled data (through today), only if scoring helped.
    if scoring_helps:
        live = {w: score_wallet(tr, res, now) for w, tr in trades_by_wallet.items()}
        keep = sorted((w for w, s in live.items() if passes(s)), key=lambda w: -live[w]["pnl"])
        with open(WALLETS_FILE, "w") as f:
            json.dump({"generated_at": now, "wallets": [
                {"wallet": w, "name": pool[w]["name"], "pnl": round(live[w]["pnl"]),
                 "roi": round(live[w]["roi"], 4), "markets": live[w]["markets"]} for w in keep]},
                f, indent=1)
        log(f"Wrote {WALLETS_FILE} with {len(keep)} wallets")

    tg = ["<b>🧪 PolyTail backtest done</b>", verdict.replace("**", ""), ""]
    for r in table:
        if r["wallets"] == "scored" and r["min_pos"] == 1_000:
            tg.append(f"N={r['N']}: {r['settled']} bets, {r['win_rate']:.0%} wins, "
                      f"{pct(r['mean_roi'])}/bet")
    tg.append("\nFull report: results/backtest_report.md in your repo")
    send_telegram("\n".join(tg))
    print(report)


if __name__ == "__main__":
    main()
