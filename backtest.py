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

from common import get_json, get_pages, market_resolutions, money, num, send_telegram

# ---------------------------------------------------------------- settings
LOOKBACK_DAYS = int(os.environ.get("BT_LOOKBACK_DAYS", 240))
TEST_DAYS = int(os.environ.get("BT_TEST_DAYS", 90))
POOL_DEPTH = int(os.environ.get("BT_POOL_DEPTH", 100))   # per leaderboard
CATEGORY = os.environ.get("BT_CATEGORY", "overall") or "overall"   # "overall" or "sports"
SPORTS = CATEGORY == "sports"   # sports: only game markets, signals before kickoff
POOL_BOARDS = [("ALL", "PNL"), ("MONTH", "PNL"), ("ALL", "VOLUME"), ("MONTH", "VOLUME")]

MAX_TRADES_PER_WALLET = int(os.environ.get("BT_MAX_TRADES", 50_000))   # more = bot / market maker, skip
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

CACHE_DIR = os.environ.get("BT_CACHE", "cache")
OUT_DIR = os.environ.get("POLYTAIL_RESULTS", "results" if not SPORTS else "results/sports")
SHARP_FILE = "wallets_sharp.json" if not SPORTS else "wallets_sports_sharp.json"
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
        rows = get_json("/v2/leaderboard", {"category": CATEGORY, "time_period": period.lower(),
                                            "sort_by": order, "limit": POOL_DEPTH}) or []
        for r in rows:
            w = (r.get("user_id") or "").lower()
            if w:
                pool.setdefault(w, {"name": r.get("user_name") or w[:8]})
    return pool


def _trade_row(wallet, t):
    idx = int(num(t.get("outcome_index"), -1))
    return {
        "wallet": wallet, "ts": num(t.get("timestamp")), "side": t.get("side"),
        "cid": t.get("condition_id"), "idx": -1 if idx == 999 else idx,
        "asset": t.get("token_id"), "size": num(t.get("size")),
        "price": num(t.get("price")), "title": t.get("title") or "",
        "outcome": t.get("outcome") or "", "slug": t.get("event_slug") or "",
        "tx": t.get("transaction_hash"),
    }


def _fetch_trades(wallet, start, end):
    rows, complete = get_pages("/v2/trades", {
        "user": wallet, "start": int(start), "end": int(end),
        "taker_only": "false", "limit": 1000,
    }, max_rows=MAX_TRADES_PER_WALLET + 1)
    if not complete and len(rows) > MAX_TRADES_PER_WALLET:
        return None  # bot / market maker
    return [_trade_row(wallet, t) for t in rows]


def wallet_trades(wallet, start, end, now):
    """All of a wallet's fills (maker + taker) between start and end, oldest first.
    Cached per wallet; later runs only download what's new."""
    name = f"trades_{wallet}.json"
    cached = cache_get(name)
    if cached and cached.get("start", 1e18) <= start:
        new = _fetch_trades(wallet, cached["end"] - DAY, end)
        if new is None:
            return None
        trades = cached["trades"] + new
    else:
        trades = _fetch_trades(wallet, start, end)
        if trades is None:
            return None
    seen, out = set(), []
    for t in trades:
        k = (t["tx"], t["asset"], t["side"], t["size"], t["price"], t["ts"])
        if k not in seen and start <= t["ts"] < end:
            seen.add(k)
            out.append(t)
    if len(out) > MAX_TRADES_PER_WALLET:
        return None
    out.sort(key=lambda t: t["ts"])
    cache_put(name, {"start": start, "end": now, "trades": out})
    return out


def price_after(asset, ts, lookups):
    """Market price DELAY_MINUTES after ts, from Polymarket's price history."""
    key = f"{asset}_{int(ts // 300)}"
    if key in lookups["cache"]:
        return lookups["cache"][key]
    if lookups["count"] >= MAX_PRICE_LOOKUPS:
        return None
    lookups["count"] += 1
    rows = get_json("/v2/prices-history", {"token_id": asset,
                                           "as_of": int(ts + DELAY_MINUTES * 60)}) or []
    p = num(rows[0].get("price"), None) if rows and isinstance(rows, list) else None
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


# ---------------------------------------------------------------- sharpness (CLV)
CLV_MIN_COST = 500         # only measure bets of at least $500
CLV_PER_WALLET = int(os.environ.get("BT_CLV_PER_WALLET", 100))  # most recent N markets per wallet per window
CLV_MIN_BETS = 20          # need this many measured bets to judge a wallet
CLV_MIN_MEAN = 0.01        # beat the close by 1c+ on average...
CLV_MIN_T = 2.0            # ...consistently (t-stat), not from a couple of lucky moves


def clv_ref_time(entry_ts, info):
    """The 'closing' moment we compare a bet against."""
    if info.get("sport") and info.get("game_start") and entry_ts < info["game_start"]:
        return info["game_start"] - 60              # sports: last price before kickoff
    ref = entry_ts + 86400                           # other markets: price a day later
    if info.get("resolved_at"):
        ref = min(ref, info["resolved_at"] - 3600)   # never peek at the settled price
    return ref if ref > entry_ts else None


def clv_jobs(trades, res, before):
    """One job per (market, side) the wallet bought before `before`: avg entry vs. close."""
    per = {}
    for t in trades:
        if t["side"] != "BUY" or t["idx"] < 0 or not t["asset"]:
            continue
        info = res.get(t["cid"])
        if not info:
            continue
        k = (t["cid"], t["idx"])
        j = per.setdefault(k, {"asset": t["asset"], "first": t["ts"], "cost": 0.0,
                               "shares": 0.0, "info": info})
        ref = clv_ref_time(j["first"], info)
        if ref is None or t["ts"] >= ref:
            continue                                 # only buys made before the close
        j["cost"] += t["size"] * t["price"]
        j["shares"] += t["size"]
    out = []
    for k, j in per.items():
        ref = clv_ref_time(j["first"], j["info"])
        if ref is None or ref >= before or j["cost"] < CLV_MIN_COST or not j["shares"]:
            continue
        out.append({"key": k, "asset": j["asset"], "ref": ref, "cost": j["cost"],
                    "entry": j["cost"] / j["shares"]})
    out.sort(key=lambda j: -j["ref"])
    return out[:CLV_PER_WALLET]


def fetch_close_prices(jobs, cache):
    """Fill job['close'] from price history (parallel, cached)."""
    from concurrent.futures import ThreadPoolExecutor

    def key(j):
        return f"{j['asset']}_{int(j['ref'] // 300)}"

    todo = list({key(j): j for j in jobs if key(j) not in cache}.values())

    def fetch(j):
        rows = get_json("/v2/prices-history", {"token_id": j["asset"], "as_of": int(j["ref"])}) or []
        return key(j), (num(rows[0].get("price"), None) if rows and isinstance(rows, list) else None)

    with ThreadPoolExecutor(max_workers=8) as pool:
        for i, (k, p) in enumerate(pool.map(fetch, todo), 1):
            cache[k] = p
            if i % 1000 == 0:
                log(f"  closing prices fetched: {i}/{len(todo)}")
    for j in jobs:
        j["close"] = cache.get(key(j))


def clv_score(jobs):
    xs = [(j["close"] - j["entry"], j["cost"]) for j in jobs if j.get("close") is not None]
    n = len(xs)
    if n < 2:
        return {"clv_n": n, "clv_mean": 0.0, "clv_beat": 0.0, "clv_t": 0.0}
    mean = sum(d for d, _ in xs) / n
    sd = math.sqrt(sum((d - mean) ** 2 for d, _ in xs) / (n - 1)) or 1e-9
    return {"clv_n": n, "clv_mean": mean, "clv_beat": sum(d > 0 for d, _ in xs) / n,
            "clv_t": mean / (sd / math.sqrt(n))}


def is_profitable(s):
    """Real winnings on settled markets: $5K+ profit and a positive return."""
    return s["markets"] >= 10 and s["pnl"] >= MIN_TRAIN_PNL and s["roi"] > 0


def is_sharp(s):
    return s["clv_n"] >= CLV_MIN_BETS and s["clv_mean"] >= CLV_MIN_MEAN and s["clv_t"] >= CLV_MIN_T


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
        if SPORTS and not (info and info.get("sport") and info.get("game_start")
                           and s["ts"] < info["game_start"]):
            continue  # sports test: only pre-kickoff signals on game markets
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

    from concurrent.futures import ThreadPoolExecutor
    trades_by_wallet, bots = {}, 0
    with ThreadPoolExecutor(max_workers=4) as ex:
        for i, (w, tr) in enumerate(zip(pool, ex.map(lambda w: wallet_trades(w, start, now, now), pool)), 1):
            if tr is None:
                bots += 1
            elif tr:
                trades_by_wallet[w] = tr
            if i % 25 == 0:
                log(f"  trades pulled for {i}/{len(pool)} wallets")
    log(f"Usable wallets: {len(trades_by_wallet)} (skipped {bots} bot-like)")

    res_cache = cache_get("resolutions_v2.json") or {}
    all_cids = {t["cid"] for tr in trades_by_wallet.values() for t in tr}
    log(f"Looking up results for {len(all_cids)} markets")
    res = market_resolutions(list(all_cids), cache=res_cache)
    cache_put("resolutions_v2.json", {k: v for k, v in res_cache.items() if v})
    log(f"{len(res)} markets settled")

    # Score wallets on training data only.
    scores = {w: score_wallet(tr, res, cutoff) for w, tr in trades_by_wallet.items()}
    selected = {w for w, s in scores.items() if passes(s)}
    log(f"Selected {len(selected)} wallets from training window")

    # Sharpness: does each wallet beat the closing price? Training-window bets only for
    # the test (no peeking); a second pass over all bets builds the live sharp list.
    lookups = {"cache": cache_get("prices.json") or {}, "count": 0}
    train_jobs = {w: clv_jobs(tr, res, cutoff) for w, tr in trades_by_wallet.items()}
    live_jobs = {w: clv_jobs(tr, res, now) for w, tr in trades_by_wallet.items()}
    all_jobs = [j for js in list(train_jobs.values()) + list(live_jobs.values()) for j in js]
    log(f"Measuring closing-line value on {len(all_jobs)} bets")
    fetch_close_prices(all_jobs, lookups["cache"])
    cache_put("prices.json", lookups["cache"])
    for w in scores:
        scores[w].update(clv_score(train_jobs[w]))
    sharp = {w for w, s in scores.items() if is_sharp(s)}
    log(f"Sharp by CLV (training window): {len(sharp)} wallets")
    proven = {w for w in sharp if is_profitable(scores[w])}
    log(f"Proven (sharp AND profitable): {len(proven)} wallets")

    all_trades = sorted((t for tr in trades_by_wallet.values() for t in tr), key=lambda t: t["ts"])

    sets = {"proven (profit+CLV)": proven, "sharp (CLV)": sharp, "scored": selected, "whole pool": set(trades_by_wallet)}
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
                log(f"  {set_name:18} N={n} min ${mp:>5}: {st['settled']:4} settled, "
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

    def best_of(name):
        rows = [r for r in table if r["wallets"] == name and ok(r)]
        return max(rows, key=lambda r: r["mean_roi"]) if rows else None

    sharp_best, pool_best = best_of("sharp (CLV)"), best_of("whole pool")
    sharp_helps = bool(sharp_best and sharp_best["ci_low"] == sharp_best["ci_low"]
                       and sharp_best["ci_low"] > 0
                       and (not pool_best or sharp_best["mean_roi"] > pool_best["mean_roi"]))
    proven_best = best_of("proven (profit+CLV)")
    proven_helps = bool(proven_best and proven_best["ci_low"] == proven_best["ci_low"]
                        and proven_best["ci_low"] > 0
                        and (not pool_best or proven_best["mean_roi"] > pool_best["mean_roi"]))

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
        w.writerow(["wallet", "name", "sharp_clv", "selected", "markets", "cost", "pnl", "roi",
                    "market_win_rate", "months_positive", "clv_bets", "clv_avg_cents",
                    "clv_beat_rate", "clv_t"])
        for wal, s in sorted(scores.items(), key=lambda kv: -kv[1]["clv_t"]):
            w.writerow([wal, pool[wal]["name"], wal in sharp, wal in selected, s["markets"],
                        round(s["cost"]), round(s["pnl"]), round(s["roi"], 4),
                        round(s["market_win_rate"], 3), s["months_positive"], s["clv_n"],
                        round(s["clv_mean"] * 100, 2), round(s["clv_beat"], 3),
                        round(s["clv_t"], 2)])

    lines = [
        f"# PolyTail backtest report ({CATEGORY})",
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
        f"Profit-scored wallets {'beat' if scoring_helps else 'did NOT beat'} the whole "
        "pool (N=3, $1K).",
        f"**Sharp wallets (closing-line value):** {len(sharp)} wallets beat the closing price "
        f"consistently in training ({CLV_MIN_BETS}+ bets, avg {CLV_MIN_MEAN*100:.0f}¢+, t≥{CLV_MIN_T:g}). "
        + (f"Best sharp setting: N={sharp_best['N']}, ${sharp_best['min_pos']:,} → "
           f"{pct(sharp_best['mean_roi'])}/bet over {sharp_best['settled']} bets. "
           if sharp_best else "Too few sharp signals to judge (need 30+ settled). ")
        + (f"Whole pool best: {pct(pool_best['mean_roi'])}/bet. " if pool_best else "")
        + ("**Following sharps beat following the pool.**" if sharp_helps
           else "Following sharps did NOT clearly beat the pool."),
        f"**Proven winners (profitable AND beat the close):** {len(proven)} wallets. "
        + (f"Best: N={proven_best['N']}, ${proven_best['min_pos']:,} → "
           f"{pct(proven_best['mean_roi'])}/bet over {proven_best['settled']} bets. "
           if proven_best else "Too few signals to judge (need 30+ settled). ")
        + ("**Beat the pool.**" if proven_helps else "Did NOT clearly beat the pool."),
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

    # Candidate sharp watchlist, scored on ALL bets through today. Saved for review only —
    # the live bots don't use it until it's renamed/activated with Hunter's OK.
    live_clv = {w: clv_score(js) for w, js in live_jobs.items()}
    keep = sorted((w for w, s in live_clv.items() if is_sharp(s)), key=lambda w: -live_clv[w]["clv_t"])
    live_profit = {w: score_wallet(trades_by_wallet[w], res, now) for w in keep}
    with open(SHARP_FILE, "w") as f:
        json.dump({"generated_at": now, "beat_pool_in_backtest": sharp_helps,
                   "proven_beat_pool_in_backtest": proven_helps,
                   "proven_best_setting": ({"MIN_WALLETS_AGREEING": proven_best["N"],
                                            "MIN_POSITION_USD": proven_best["min_pos"]}
                                           if proven_best else None),
                   "best_setting": ({"MIN_WALLETS_AGREEING": sharp_best["N"],
                                     "MIN_POSITION_USD": sharp_best["min_pos"]} if sharp_best else None),
                   "wallets": [{"wallet": w, "name": pool[w]["name"],
                                "pnl": round(live_profit[w]["pnl"]),
                                "proven": is_profitable(live_profit[w]),
                                "clv_avg_cents": round(live_clv[w]["clv_mean"] * 100, 2),
                                "clv_beat_rate": round(live_clv[w]["clv_beat"], 3),
                                "clv_bets": live_clv[w]["clv_n"]} for w in keep]},
                  f, indent=1)
    log(f"Wrote {SHARP_FILE} with {len(keep)} sharp wallets (not active)")

    tg = [f"<b>🧪 PolyTail backtest done ({CATEGORY})</b>", verdict.replace("**", ""), ""]
    tg.append(f"Sharp wallets (beat the close): {len(sharp)}")
    for r in table:
        if r["wallets"] == "sharp (CLV)" and r["N"] in (2, 3, 4):
            tg.append(f"Sharps N={r['N']} ${r['min_pos']:,}: {r['settled']} bets, "
                      f"{r['win_rate']:.0%} wins, {pct(r['mean_roi'])}/bet")
    tg.append("✅ Sharps beat the big-money pool" if sharp_helps else "Sharps did not clearly beat the pool")
    tg.append(f"\nProven winners (profit + beat the close): {len(proven)}")
    for r in table:
        if r["wallets"] == "proven (profit+CLV)" and r["N"] in (2, 3):
            tg.append(f"Proven N={r['N']} ${r['min_pos']:,}: {r['settled']} bets, "
                      f"{r['win_rate']:.0%} wins, {pct(r['mean_roi'])}/bet")
    tg.append("✅ Proven winners beat the pool" if proven_helps else "Proven winners did not clearly beat the pool")
    tg.append(f"\nFull report: {OUT_DIR}/backtest_report.md in your repo")
    send_telegram("\n".join(tg))
    print(report)


if __name__ == "__main__":
    main()
