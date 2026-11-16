"""
Golf model v1 — Hunter's own PGA Tour model.

1. Pulls every PGA Tour round from ESPN for the last two seasons (free, no key).
2. Rates each player in strokes per round vs. an average Tour player,
   adjusting for how hard each round played (field strength + conditions),
   weighting recent rounds more and shrinking small samples toward a prior.
3. Simulates this week's tournament many times to get win / Top 5 / Top 10 /
   Top 20 / make-cut chances and 72-hole head-to-head chances.
4. Writes golf/results/*.md + *.csv and sends a Telegram summary.

Fair odds = the price where a bet breaks even. Only bet when a book offers
BETTER than the fair price (and ideally 4%+ better).

Run:  python golf/model.py              (this week's event)
      python golf/model.py --backtest   (grade the model on past events)
"""

import csv
import json
import math
import os
import random
import sys
import time
import urllib.request
from collections import defaultdict
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from common import send_telegram
except ImportError:  # running standalone
    def send_telegram(text):
        print(text)

SCOREBOARD = "https://site.api.espn.com/apis/site/v2/sports/golf/pga/scoreboard"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")

HALF_LIFE_DAYS = 150     # a round this old counts half as much as one today
PRIOR_ROUNDS = 12        # small samples are pulled toward the prior this hard
PRIOR_SKILL = -1.0       # unknown / thin-sample players assumed 1 stroke worse than avg
SIMS = int(os.environ.get("GOLF_SIMS", "10000"))
CUT_SIZE = 65            # top 65 and ties make the cut (fields of 100+)
H2H_TOP = 80             # head-to-heads for this many best-rated players in the field
SEED = 7


# ---------------------------------------------------------------- data

def get_json(url, retries=4):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "golf-model/1.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode())
        except Exception as e:  # noqa: BLE001
            print(f"  ! {e} on {url}", file=sys.stderr)
            time.sleep(3 * (attempt + 1))
    return {}

def parse_date(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))

def rounds_from_events(events):
    """Completed 18-hole rounds: list of dicts {event_id, event, round_key, date, pid, name, score}."""
    out = []
    for e in events:
        comp = (e.get("competitions") or [{}])[0]
        start = parse_date(e["date"])
        for c in comp.get("competitors") or []:
            pid = str(c.get("id"))
            name = (c.get("athlete") or {}).get("displayName", pid)
            for ls in c.get("linescores") or []:
                holes = ls.get("linescores") or []
                val = ls.get("value")
                rnd = ls.get("period")
                if not rnd or not val or len(holes) != 18 or not (55 <= val <= 95):
                    continue
                out.append({
                    "event_id": e["id"], "event": e.get("name", ""),
                    "round_key": f"{e['id']}-{rnd}",
                    "date": start + timedelta(days=int(rnd) - 1),
                    "pid": pid, "name": name, "score": float(val),
                })
    return out

def load_seasons(years):
    events = []
    for y in years:
        body = get_json(f"{SCOREBOARD}?dates={y}")
        events += body.get("events") or []
        print(f"  {y}: {len(body.get('events') or [])} events")
    return events


# ---------------------------------------------------------------- ratings

def fit_ratings(rounds, asof):
    """
    Model: score = round_difficulty - skill + noise.
    Alternate between estimating each round's difficulty and each player's skill.
    Returns ({pid: skill}, {pid: effective_rounds}, residual_sd, names).
    """
    rounds = [r for r in rounds if r["date"] < asof]
    if not rounds:
        return {}, {}, 2.8, {}
    names = {r["pid"]: r["name"] for r in rounds}
    w = [0.5 ** ((asof - r["date"]).days / HALF_LIFE_DAYS) for r in rounds]
    by_round = defaultdict(list)
    for i, r in enumerate(rounds):
        by_round[r["round_key"]].append(i)
    skill = defaultdict(float)
    diff = {}
    for _ in range(15):
        for k, idx in by_round.items():
            diff[k] = sum(rounds[i]["score"] + skill[rounds[i]["pid"]] for i in idx) / len(idx)
        num_, den = defaultdict(float), defaultdict(float)
        for i, r in enumerate(rounds):
            num_[r["pid"]] += w[i] * (diff[r["round_key"]] - r["score"])
            den[r["pid"]] += w[i]
        skill = defaultdict(float, {
            p: (num_[p] + PRIOR_ROUNDS * PRIOR_SKILL) / (den[p] + PRIOR_ROUNDS) for p in num_})
        # keep the scale anchored: the average rated round = 0
        avg = sum(w[i] * skill[r["pid"]] for i, r in enumerate(rounds)) / sum(w)
        for p in skill:
            skill[p] -= avg
    resid = [diff[r["round_key"]] - r["score"] - skill[r["pid"]] for r in rounds]
    sd = math.sqrt(sum(x * x for x in resid) / max(1, len(resid) - 1))
    eff = {p: den[p] for p in den}
    return dict(skill), eff, sd, names


# ---------------------------------------------------------------- simulation

def simulate(field, skill, sd, sims=SIMS, cut=True, seed=SEED, h2h_on=True):
    """
    field: list of pids. Returns per-player finish probabilities and an
    h2h matrix for the best-rated H2H_TOP players.
    Ties at a cutoff are split dead-heat style, like the books settle them.
    """
    rng = random.Random(seed)
    n = len(field)
    mu = [-skill.get(p, PRIOR_SKILL) for p in field]   # lower score = better
    stats = {p: defaultdict(float) for p in field}
    top = sorted(range(n), key=lambda i: mu[i])[:H2H_TOP] if h2h_on else []
    h2h_w = defaultdict(float)   # (i, j) -> wins of i over j (ties = 0.5)
    h2h_n = defaultdict(float)
    gauss = rng.gauss
    for _ in range(sims):
        r12 = [mu[i] * 2 + gauss(0, sd) + gauss(0, sd) for i in range(n)]
        made = [True] * n
        if cut and n >= 100:
            line = sorted(r12)[min(CUT_SIZE, n) - 1]
            made = [x <= line + 1e-9 for x in r12]
        total = [r12[i] + (mu[i] * 2 + gauss(0, sd) + gauss(0, sd) if made[i] else 1000.0)
                 for i in range(n)]
        order = sorted(range(n), key=lambda i: total[i])
        # winner: a tie for first goes to a playoff (coin flip among the tied)
        best = total[order[0]]
        tied = [i for i in order if abs(total[i] - best) < 1e-9]
        stats[field[rng.choice(tied)]]["win"] += 1
        for k, label in ((5, "top5"), (10, "top10"), (20, "top20")):
            if k >= n:
                continue
            edge = total[order[k - 1]]
            better = sum(1 for i in range(n) if total[i] < edge - 1e-9)
            at = [i for i in range(n) if abs(total[i] - edge) < 1e-9]
            share = (k - better) / len(at)
            for i in order[:better]:
                stats[field[i]][label] += 1
            for i in at:
                stats[field[i]][label] += share
        for i in range(n):
            stats[field[i]]["cut"] += made[i]
        for a in range(len(top)):
            i = top[a]
            for b in range(a + 1, len(top)):
                j = top[b]
                ti = total[i] if made[i] else 1000 + r12[i]
                tj = total[j] if made[j] else 1000 + r12[j]
                if ti == tj:
                    continue  # push
                h2h_n[(i, j)] += 1
                if ti < tj:
                    h2h_w[(i, j)] += 1
    probs = {p: {k: v / sims for k, v in s.items()} for p, s in stats.items()}
    h2h = []
    for (i, j), cnt in h2h_n.items():
        pi = h2h_w[(i, j)] / cnt
        h2h.append((field[i], field[j], pi))
    return probs, h2h


# ---------------------------------------------------------------- helpers

def fair_american(p):
    if p <= 0:
        return "—"
    if p >= 1:
        return "-∞"
    return f"+{round(100 * (1 - p) / p)}" if p < 0.5 else f"{round(-100 * p / (1 - p))}"

def pct(p):
    return f"{100 * p:.1f}%" if p >= 0.001 else "<0.1%"

def upcoming_event(now):
    """Next event that hasn't finished, with its field (empty if not posted yet)."""
    for back in range(0, 3):
        day = (now - timedelta(days=back)).strftime("%Y%m%d")
        body = get_json(f"{SCOREBOARD}?dates={day}")
        for e in body.get("events") or []:
            if e.get("status", {}).get("type", {}).get("state") == "pre":
                return e
    body = get_json(SCOREBOARD)
    cal = ((body.get("leagues") or [{}])[0]).get("calendar") or []
    for item in cal:
        if parse_date(item["endDate"]) >= now - timedelta(hours=12):
            start = parse_date(item["startDate"])
            got = get_json(f"{SCOREBOARD}?dates={start.strftime('%Y%m%d')}")
            for e in got.get("events") or []:
                if e.get("id") == item["id"]:
                    return e
            return {"id": item["id"], "name": item["label"], "date": item["startDate"],
                    "competitions": [{"competitors": []}]}
    return None


# ---------------------------------------------------------------- main

def predict():
    now = datetime.now(timezone.utc)
    print("Loading rounds…")
    events = load_seasons([now.year - 1, now.year])
    rounds = rounds_from_events(events)
    print(f"  {len(rounds)} completed rounds")
    ev = upcoming_event(now)
    if not ev:
        send_telegram("<b>⛳ Golf model</b>\nNo upcoming PGA Tour event found.")
        return
    comp = (ev.get("competitions") or [{}])[0]
    field_rows = comp.get("competitors") or []
    skill, eff, sd, names = fit_ratings(rounds, now)
    for c in field_rows:
        names.setdefault(str(c["id"]), (c.get("athlete") or {}).get("displayName", str(c["id"])))
    field = [str(c["id"]) for c in field_rows]
    title = f"{ev.get('name')} ({ev.get('date', '')[:10]})"
    os.makedirs(OUT_DIR, exist_ok=True)
    if not field:
        msg = (f"<b>⛳ Golf model — {title}</b>\nField not posted yet; will retry on the "
               f"next scheduled run. Round-to-round SD {sd:.2f} strokes.")
        send_telegram(msg)
        with open(os.path.join(OUT_DIR, "predictions.md"), "w") as f:
            f.write(f"# Golf model — {title}\n\nField not posted yet.\n")
        return
    probs, h2h = simulate(field, skill, sd)
    rows = []
    for p in field:
        pr = probs[p]
        rows.append({
            "player": names.get(p, p), "espn_id": p,
            "rating": round(skill.get(p, PRIOR_SKILL), 2),
            "rounds_weighted": round(eff.get(p, 0), 1),
            "win": pr.get("win", 0), "top5": pr.get("top5", 0), "top10": pr.get("top10", 0),
            "top20": pr.get("top20", 0), "make_cut": pr.get("cut", 0),
        })
    rows.sort(key=lambda r: -r["win"])

    with open(os.path.join(OUT_DIR, "predictions.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) + [
            "fair_win", "fair_top10", "fair_top20"])
        w.writeheader()
        for r in rows:
            w.writerow({**r, **{k: round(r[k], 4) for k in ("win", "top5", "top10", "top20", "make_cut")},
                        "fair_win": fair_american(r["win"]), "fair_top10": fair_american(r["top10"]),
                        "fair_top20": fair_american(r["top20"])})
    with open(os.path.join(OUT_DIR, "matchups.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["player_a", "player_b", "a_win_prob", "fair_a", "fair_b"])
        for a, b, pa in sorted(h2h, key=lambda x: (names.get(x[0], ""), names.get(x[1], ""))):
            w.writerow([names.get(a, a), names.get(b, b), round(pa, 4),
                        fair_american(pa), fair_american(1 - pa)])

    stamp = now.strftime("%Y-%m-%d %H:%M UTC")
    md = [f"# Golf model — {title}", "",
          f"Run {stamp}. {len(field)} players, {SIMS:,} simulations. "
          f"Rating = strokes per round better than an average PGA Tour player.",
          "Fair odds = break-even price. Only bet if a book beats it, ideally by 4%+.", "",
          "| # | Player | Rating | Win | Fair | Top 10 | Fair | Top 20 | Fair | Cut |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(rows[:60], 1):
        thin = "*" if r["rounds_weighted"] < 15 else ""
        md.append(f"| {i} | {r['player']}{thin} | {r['rating']:+.2f} | {pct(r['win'])} | "
                  f"{fair_american(r['win'])} | {pct(r['top10'])} | {fair_american(r['top10'])} | "
                  f"{pct(r['top20'])} | {fair_american(r['top20'])} | {pct(r['make_cut'])} |")
    md += ["", "\\* thin recent sample — rating leans on the prior, trust it less.",
           "", "Head-to-head (72-hole) fair odds for the top players: see matchups.csv.",
           "", "v1 limits: no course-fit or course-history adjustment yet; PGA Tour rounds only "
           "(players coming from other tours look worse than they are)."]
    with open(os.path.join(OUT_DIR, "predictions.md"), "w") as f:
        f.write("\n".join(md) + "\n")

    tg = [f"<b>⛳ Golf model — {title}</b>", "Win% · fair · Top20% · fair"]
    for r in rows[:15]:
        tg.append(f"{r['player']}: {pct(r['win'])} {fair_american(r['win'])} · "
                  f"{pct(r['top20'])} {fair_american(r['top20'])}")
    tg.append("\nFull table + matchups: golf/results/ in the repo. Bet only if a book beats the fair price.")
    send_telegram("\n".join(tg))
    print("\n".join(md[:30]))


def backtest(n_events=12):
    """Re-run the model on recent finished events using only data from before each one."""
    now = datetime.now(timezone.utc)
    events = load_seasons([now.year - 1, now.year])
    rounds = rounds_from_events(events)
    done = [e for e in events if e.get("status", {}).get("type", {}).get("completed")]
    done = sorted(done, key=lambda e: e["date"])[-n_events:]
    lines, briers = [], defaultdict(lambda: [0.0, 0.0, 0])
    corr_all = []
    for e in done:
        start = parse_date(e["date"])
        skill, _, sd, _ = fit_ratings(rounds, start)
        comp = e["competitions"][0]
        field, finish = [], {}
        for c in comp.get("competitors") or []:
            pid = str(c["id"])
            ls = [x for x in c.get("linescores") or [] if len(x.get("linescores") or []) == 18]
            if not ls:
                continue
            field.append(pid)
            finish[pid] = (int(c.get("order") or 999), len(ls))
        if len(field) < 30:
            continue
        probs, _ = simulate(field, skill, sd, sims=3000, seed=1, h2h_on=False)
        n = len(field)
        for label, k in (("top20", 20), ("top10", 10), ("cut", None)):
            for p in field:
                pos, nr = finish[p]
                hit = (nr >= 3) if k is None else (pos <= k)
                pr = probs[p].get(label, 0)
                base = (min(CUT_SIZE, n) / n) if k is None else k / n
                briers[label][0] += (pr - hit) ** 2
                briers[label][1] += (base - hit) ** 2
                briers[label][2] += 1
        # rank correlation of rating vs finish
        xs = [skill.get(p, PRIOR_SKILL) for p in field]
        ys = [-finish[p][0] for p in field]
        rx = {v: i for i, v in enumerate(sorted(range(n), key=lambda i: xs[i]))}
        ry = {v: i for i, v in enumerate(sorted(range(n), key=lambda i: ys[i]))}
        d2 = sum((rx[i] - ry[i]) ** 2 for i in range(n))
        rho = 1 - 6 * d2 / (n * (n * n - 1))
        corr_all.append(rho)
        lines.append(f"  {e['name'][:38]:38} rank corr {rho:+.2f}")
    out = ["<b>⛳ Golf model backtest</b>", f"Last {len(corr_all)} finished PGA Tour events, "
           "rated only on rounds before each event:"]
    out += lines
    if corr_all:
        out.append(f"\nAvg rank correlation (rating vs finish): {sum(corr_all)/len(corr_all):+.2f}")
    for label, (b, b0, cnt) in briers.items():
        if cnt and b0:
            out.append(f"{label}: model error {b/cnt:.4f} vs no-skill guess {b0/cnt:.4f} "
                       f"({(1 - b / b0):+.0%} better)")
    out.append("(Positive % = model knows more than a coin-flip guess. "
               "Beating the sportsbooks is a higher bar — that's what CLV tracking tests.)")
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "backtest.md"), "w") as f:
        f.write("# Golf model backtest\n\n" + "\n".join(x.replace("<b>", "").replace("</b>", "")
                                                    for x in out[1:]) + "\n")
    send_telegram("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    if "--backtest" in sys.argv:
        backtest()
    else:
        predict()
