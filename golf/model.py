"""
Golf model v2 — Hunter's own PGA Tour model.

1. Pulls every round from ESPN for the last four seasons on FOUR tours:
   PGA Tour, DP World Tour, Korn Ferry Tour and LIV (free, no key). Players who
   cross between tours link the tours together, so everyone is rated on one scale.
2. Rates each player in strokes per round vs. an average PGA Tour player,
   adjusting for how hard each round played (field strength + conditions),
   weighting recent rounds more and shrinking small samples toward a prior.
   Each player also gets his own round-to-round volatility.
3. Simulates this week's tournament many times (whole-stroke scores, real cut
   rules incl. ties) to get win / Top 5 / Top 10 /
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

TOURS = ["pga", "eur", "ntw", "liv"]   # PGA, DP World, Korn Ferry, LIV (ESPN league codes)
SEASONS_BACK = 3         # this season + 3 before it
# The four numbers below were chosen on 2024-25 events and confirmed on untouched 2026 events.
HALF_LIFE_DAYS = 250     # a round this old counts half as much as one today
PRIOR_ROUNDS = 3         # small samples are pulled toward the prior this hard
PRIOR_SKILL = -3.0       # unknown / thin-sample players assumed 3 strokes worse than avg
VAR_PRIOR_ROUNDS = 40    # how hard a player's own volatility is pulled toward the tour average
BASE_SCORE = 70.5        # only used to turn simulated scores into whole strokes
TEAM_WORDS = ("zurich", "presidents cup", "ryder cup", "the match", "showdown", "hero cup",
              "team cup", "match play", "shootout", "grant thornton", "q-school")
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
    """Completed 18-hole rounds: list of dicts {event_id, event, round_key, date, pid, name, score, tour}."""
    out = []
    for e in events:
        comp = (e.get("competitions") or [{}])[0]
        start = parse_date(e["date"])
        name_l = (e.get("name") or "").lower()
        comps = comp.get("competitors") or []
        if len(comps) < 20 or any(w in name_l for w in TEAM_WORDS):
            continue   # team / match-play / exhibition events are not individual stroke play
        # some tours' feeds carry round totals without hole-by-hole detail; accept those rounds
        # only when the whole event has no hole detail (so half-finished rounds never slip in)
        any18 = any(len(ls.get("linescores") or []) == 18
                    for c in comps for ls in c.get("linescores") or [])
        for c in comps:
            pid = str(c.get("id"))
            name = (c.get("athlete") or {}).get("displayName", pid)
            for ls in c.get("linescores") or []:
                holes = ls.get("linescores") or []
                val = ls.get("value")
                rnd = ls.get("period")
                if rnd not in (1, 2, 3, 4) or not val or not (55 <= val <= 95):
                    continue
                if len(holes) != 18 and not (len(holes) == 0 and not any18):
                    continue
                out.append({
                    "event_id": e["id"], "event": e.get("name", ""),
                    "round_key": f"{e['id']}-{rnd}",
                    "date": start + timedelta(days=int(rnd) - 1),
                    "pid": pid, "name": name, "score": float(val),
                    "tour": e.get("_tour", "pga"),
                })
    return out

def load_seasons(years, tours=("pga",)):
    """Events for the given seasons. PGA events come first; an event on another tour that is
    really the same tournament (co-sanctioned: same week, mostly the same players) is dropped."""
    events = []
    for tour in tours:
        url = SCOREBOARD.replace("/pga/", f"/{tour}/")
        for y in years:
            got = (get_json(f"{url}?dates={y}").get("events") or [])
            ok = []
            for e in got:
                try:                       # a few unscheduled events have no usable date
                    parse_date(e["date"])
                except (KeyError, ValueError, AttributeError):
                    continue
                e["_tour"] = tour
                ok.append(e)
            got = ok
            events += got
            print(f"  {tour} {y}: {len(got)} events")
    def ids(e):
        return {str(c.get("id")) for c in ((e.get("competitions") or [{}])[0].get("competitors") or [])}
    order = {t: i for i, t in enumerate(tours)}
    events.sort(key=lambda e: (e["date"][:10], order[e["_tour"]]))
    keep = []
    for e in events:
        mine, d = ids(e), parse_date(e["date"])
        dup = False
        for k in keep[-12:]:
            if k["_tour"] != e["_tour"] and abs((parse_date(k["date"]) - d).days) <= 1:
                theirs = ids(k)
                if mine and theirs and len(mine & theirs) / min(len(mine), len(theirs)) > 0.5:
                    dup = True
                    break
        if not dup:
            keep.append(e)
    return keep

def seasons(now):
    return list(range(now.year - SEASONS_BACK, now.year + 1))

def cut_size(event_name, n):
    """How many players (plus ties) make the 36-hole cut; None = no cut."""
    nm = (event_name or "").lower()
    if "masters" in nm:
        return 50
    if "u.s. open" in nm:
        return 60
    if nm.strip() in ("the open", "the open championship") or "pga championship" in nm:
        return 70
    if n >= 100:
        return CUT_SIZE
    if n >= 60 and any(x in nm for x in ("genesis invitational", "arnold palmer", "memorial tournament")):
        return 50
    return None


# ---------------------------------------------------------------- ratings

def fit_ratings(rounds, asof):
    """
    Model: score = round_difficulty - skill + noise.
    Alternate between estimating each round's difficulty and each player's skill.
    Returns ({pid: skill}, {pid: effective_rounds}, residual_sd, names, {pid: own_sd}).
    Ratings are anchored so the average PGA Tour round = 0.
    """
    rounds = [r for r in rounds if r["date"] < asof]
    if not rounds:
        return {}, {}, 2.8, {}, {}
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
        pga = [i for i, r in enumerate(rounds) if r.get("tour", "pga") == "pga"] or range(len(rounds))
        avg = sum(w[i] * skill[rounds[i]["pid"]] for i in pga) / sum(w[i] for i in pga)
        for p in skill:
            skill[p] -= avg
    resid = [diff[r["round_key"]] - r["score"] - skill[r["pid"]] for r in rounds]
    sd = math.sqrt(sum(x * x for x in resid) / max(1, len(resid) - 1))
    eff = {p: den[p] for p in den}
    # each player's own volatility: recency-weighted, pulled toward the overall figure
    gv = sum(w[i] * x * x for i, x in enumerate(resid)) / sum(w)
    vnum = defaultdict(float)
    for i, r in enumerate(rounds):
        vnum[r["pid"]] += w[i] * resid[i] * resid[i]
    sd_i = {p: math.sqrt((vnum[p] + VAR_PRIOR_ROUNDS * gv) / (den[p] + VAR_PRIOR_ROUNDS)) for p in den}
    return dict(skill), eff, sd, names, sd_i


# ---------------------------------------------------------------- simulation

def simulate(field, skill, sd, sims=SIMS, cut=True, seed=SEED, h2h_on=True, sd_i=None, cut_n=CUT_SIZE):
    """
    field: list of pids. Returns per-player finish probabilities and an
    h2h matrix for the best-rated H2H_TOP players.
    Ties at a cutoff are split dead-heat style, like the books settle them.
    Scores are whole strokes, so ties (and "top N and ties" cuts) happen as often as in real life.
    sd_i: optional {pid: own round-to-round sd}; cut_n: cut size (None/0 = no cut).
    """
    rng = random.Random(seed)
    n = len(field)
    mu = [-skill.get(p, PRIOR_SKILL) for p in field]   # lower score = better
    stats = {p: defaultdict(float) for p in field}
    top = sorted(range(n), key=lambda i: mu[i])[:H2H_TOP] if h2h_on else []
    h2h_w = defaultdict(float)   # (i, j) -> wins of i over j (ties = 0.5)
    h2h_n = defaultdict(float)
    gauss = rng.gauss
    sds = [(sd_i or {}).get(p, sd) for p in field]
    floor = math.floor
    def rd(i):   # one whole-stroke round
        return floor(BASE_SCORE + mu[i] + gauss(0, sds[i]) + 0.5)
    for _ in range(sims):
        r12 = [rd(i) + rd(i) for i in range(n)]
        made = [True] * n
        if cut and cut_n and n > cut_n:
            line = sorted(r12)[cut_n - 1]
            made = [x <= line + 1e-9 for x in r12]
        total = [r12[i] + (rd(i) + rd(i) if made[i] else 1000.0)
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
    """Next event that hasn't started yet (or started < 18h ago), with its field (empty if not posted)."""
    body = get_json(SCOREBOARD)
    cal = ((body.get("leagues") or [{}])[0]).get("calendar") or []
    for item in sorted(cal, key=lambda x: x["startDate"]):
        if parse_date(item["startDate"]) >= now - timedelta(hours=18):
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
    events = load_seasons(seasons(now), TOURS)
    rounds = rounds_from_events(events)
    print(f"  {len(rounds)} completed rounds")
    ev = upcoming_event(now)
    if not ev:
        send_telegram("<b>⛳ Golf model</b>\nNo upcoming PGA Tour event found.")
        return
    comp = (ev.get("competitions") or [{}])[0]
    field_rows = comp.get("competitors") or []
    skill, eff, sd, names, sd_i = fit_ratings(rounds, now)
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
    probs, h2h = simulate(field, skill, sd, sd_i=sd_i, cut_n=cut_size(ev.get("name"), len(field)))
    rows = []
    for p in field:
        pr = probs[p]
        rows.append({
            "player": names.get(p, p), "espn_id": p,
            "rating": round(skill.get(p, PRIOR_SKILL), 2),
            "rounds_weighted": round(eff.get(p, 0), 1),
            "volatility": round(sd_i.get(p, sd), 2),
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
           "", "v2: rounds from PGA, DP World, Korn Ferry and LIV on one scale; each player has his own "
           "volatility. Course fit / course history were tested and left out (no measurable gain).",
           "Outright winner prices: the books' odds are better than this model — don't bet outrights off it."]
    with open(os.path.join(OUT_DIR, "predictions.md"), "w") as f:
        f.write("\n".join(md) + "\n")

    tg = [f"<b>⛳ Golf model — {title}</b>", "Win% · fair · Top20% · fair"]
    for r in rows[:15]:
        tg.append(f"{r['player']}: {pct(r['win'])} {fair_american(r['win'])} · "
                  f"{pct(r['top20'])} {fair_american(r['top20'])}")
    tg.append("\nFull table + matchups: golf/results/ in the repo. Bet only if a book beats the fair price.")
    send_telegram("\n".join(tg))
    print("\n".join(md[:30]))


def backtest(n_events=40):
    """Re-run the model on recent finished events using only data from before each one."""
    now = datetime.now(timezone.utc)
    events = load_seasons(seasons(now), TOURS)
    rounds = rounds_from_events(events)
    done = [e for e in events if e.get("_tour") == "pga"
            and e.get("status", {}).get("type", {}).get("completed")
            and not any(w in (e.get("name") or "").lower() for w in TEAM_WORDS)]
    done = sorted(done, key=lambda e: e["date"])[-n_events:]
    lines, briers = [], defaultdict(lambda: [0.0, 0.0, 0])
    corr_all = []
    calib = defaultdict(lambda: [0.0, 0.0, 0])   # Top-20 calibration buckets
    for e in done:
        start = parse_date(e["date"])
        skill, _, sd, _, sd_i = fit_ratings(rounds, start)
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
        n = len(field)
        cn = cut_size(e.get("name"), n)
        probs, _ = simulate(field, skill, sd, sims=3000, seed=1, h2h_on=False, sd_i=sd_i, cut_n=cn)
        for label, k in (("top20", 20), ("top10", 10), ("cut", None)):
            if k is None and not cn:
                continue
            for p in field:
                pos, nr = finish[p]
                hit = (nr >= 3) if k is None else (pos <= k)
                pr = probs[p].get(label, 0)
                base = (min(cn, n) / n) if k is None else k / n
                if label == "top20":
                    b = calib[min(int(pr * 10), 5)]
                    b[0] += pr; b[1] += hit; b[2] += 1
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
    out.append("\nTop-20 calibration (what the model said vs what happened):")
    for b in sorted(calib):
        s_p, s_h, c = calib[b]
        out.append(f"  said {s_p / c:.0%} -> happened {s_h / c:.0%}  ({c} player-events)")
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
