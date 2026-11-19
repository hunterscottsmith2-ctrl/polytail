"""Shared helpers for PolyTail: Polymarket API calls, market resolutions, Telegram."""

import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

DATA_API = "https://data-api.polymarket.com"
GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"
USER_AGENT = "polytail/2.0"


def get_json(path, params, base=DATA_API, retries=4):
    """GET a JSON endpoint. Returns [] on repeated failure so callers can keep going."""
    url = f"{base}{path}?{urllib.parse.urlencode(params, doseq=True)}"
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=30) as r:
                body = json.loads(r.read().decode())
            if isinstance(body, dict) and "data" in body:  # v2-style envelope
                body = body["data"]
            return body
        except urllib.error.HTTPError as e:
            if e.code in (400, 404, 410):  # bad params / retired route — retrying won't help
                print(f"  ! {e.code} on {url}: {e.read()[:200]!r}", file=sys.stderr)
                return []
            wait = int(e.headers.get("Retry-After") or 0) if e.code in (429, 503) else 0
            time.sleep(max(wait, 2 * (attempt + 1)))
        except Exception:  # noqa: BLE001
            time.sleep(2 * (attempt + 1))
    print(f"  ! giving up on {url}", file=sys.stderr)
    return []


def get_pages(path, params, base=DATA_API, max_rows=None, max_pages=200):
    """Follow Data API v2 cursor pagination. Returns (rows, complete)."""
    rows, cursor = [], None
    for _ in range(max_pages):
        p = dict(params)
        if cursor:
            p["cursor"] = cursor
        body = get_json_raw(path, p, base=base)
        if not isinstance(body, dict):
            return rows, False
        rows.extend(body.get("data") or [])
        cursor = (body.get("pagination") or {}).get("next_cursor")
        if not cursor:
            return rows, True
        if max_rows and len(rows) >= max_rows:
            return rows, False
        time.sleep(0.1)
    return rows, False


def get_json_raw(path, params, base=DATA_API, retries=4):
    """Like get_json but keeps the {data, pagination} envelope."""
    url = f"{base}{path}?{urllib.parse.urlencode(params, doseq=True)}"
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code in (400, 404, 410):
                print(f"  ! {e.code} on {url}: {e.read()[:200]!r}", file=sys.stderr)
                return None
            wait = int(e.headers.get("Retry-After") or 0) if e.code in (429, 503) else 0
            time.sleep(max(wait, 2 * (attempt + 1)))
        except Exception:  # noqa: BLE001
            time.sleep(2 * (attempt + 1))
    print(f"  ! giving up on {url}", file=sys.stderr)
    return None


def num(x, default=0.0):
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def parse_time(s):
    """Parse the assorted timestamp formats Polymarket returns into epoch seconds."""
    if s is None or s == "":
        return None
    if isinstance(s, (int, float)):
        return float(s)
    s = str(s).strip().replace("Z", "+00:00")
    if s.endswith("+00"):
        s += ":00"
    for candidate in (s, s.replace(" ", "T")):
        try:
            dt = datetime.fromisoformat(candidate)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.timestamp()
        except ValueError:
            continue
    return None


def _json_list(v):
    if isinstance(v, list):
        return v
    try:
        return json.loads(v or "[]")
    except (TypeError, json.JSONDecodeError):
        return []


def _sport_fields(m):
    """Game markets (moneyline / spread / total) carry a market type and a kickoff time."""
    return {"sport": bool(m.get("sportsMarketType")),
            "game_start": parse_time(m.get("gameStartTime"))}


def side_of(title, outcome, slug, condition_id, outcome_index):
    """(axis, direction) for a bet, so bets on the same game line up across markets.

    Every moneyline and spread for one game shares a "team" axis: Pistons -4.5 and Pistons ML
    both lean Pistons; Pelicans +5.5 leans the other way. Every full-game total line shares a
    "total" axis (Over / Under). Anything else is its own axis, one market at a time.
    A wallet with more than one direction on an axis is hedged (or middling) on that game."""
    title = (title or "").strip()
    outcome = (outcome or "").strip().lower()
    if slug and outcome:
        if re.match(r"Spread:", title) or (re.search(r"\s+vs\.?\s+", title)
                                           and ":" not in title and "?" not in title):
            return f"{slug}|team", outcome
        if "O/U" in title and outcome in ("over", "under"):
            return f"{slug}|total|{title.split('O/U')[0].strip()}", outcome
    return str(condition_id), str(outcome_index)


def market_info(condition_ids):
    """Sports info for open (or any) markets: {cid: {"sport": bool, "game_start": epoch|None}}."""
    out, ids = {}, [c for c in dict.fromkeys(condition_ids) if c]
    for i in range(0, len(ids), 25):
        rows = get_json("/markets", {"condition_ids": ids[i:i + 25], "limit": 100},
                        base=GAMMA_API) or []
        for m in rows:
            if m.get("conditionId"):
                out[m["conditionId"]] = _sport_fields(m)
        time.sleep(0.1)
    return out


def market_resolutions(condition_ids, cache=None):
    """
    Look up final results for markets.
    Returns {condition_id: {"values": [payout per outcome], "resolved_at": epoch or None,
                            "outcomes": [...], "title": str}}
    Only markets that are closed with a clear result are included. A payout is
    1.0 for the winner, 0.0 for losers (0.5 each for a 50/50 void).
    """
    cache = cache if cache is not None else {}
    todo = [c for c in dict.fromkeys(condition_ids) if c and c not in cache]
    for i in range(0, len(todo), 25):
        batch = todo[i:i + 25]
        rows = get_json("/markets", {"condition_ids": batch, "closed": "true",
                                      "limit": 100}, base=GAMMA_API) or []
        for m in rows:
            cid = m.get("conditionId")
            prices = [num(p) for p in _json_list(m.get("outcomePrices"))]
            if not cid or not m.get("closed") or not prices:
                continue
            if max(prices) >= 0.98:
                values = [1.0 if p >= 0.98 else 0.0 for p in prices]
            elif all(0.45 <= p <= 0.55 for p in prices):
                values = [0.5] * len(prices)
            else:
                continue  # closed but result not final yet
            cache[cid] = {
                "values": values,
                "resolved_at": parse_time(m.get("closedTime")) or parse_time(m.get("endDate")),
                "outcomes": _json_list(m.get("outcomes")),
                "title": m.get("question") or "",
                **_sport_fields(m),
            }
        for cid in batch:  # remember misses this run so we don't re-ask
            cache.setdefault(cid, None)
        time.sleep(0.2)
    return {c: cache[c] for c in condition_ids if cache.get(c)}


def send_telegram(text):
    token, chat = os.environ.get("TELEGRAM_BOT_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat:
        print("---- (no Telegram secrets set; printing instead) ----\n" + text + "\n")
        return True
    for chunk_start in range(0, len(text), 4000):  # Telegram max is 4096 chars
        data = urllib.parse.urlencode({
            "chat_id": chat, "text": text[chunk_start:chunk_start + 4000],
            "parse_mode": "HTML", "disable_web_page_preview": "true",
        }).encode()
        try:
            req = urllib.request.Request(
                f"https://api.telegram.org/bot{token}/sendMessage", data=data,
                headers={"User-Agent": USER_AGENT})
            urllib.request.urlopen(req, timeout=20).read()
        except Exception as e:  # noqa: BLE001
            print(f"  ! Telegram send failed: {e}", file=sys.stderr)
            return False
    return True


def money(x):
    sign = "-" if x < 0 else ""
    x = abs(x)
    if x >= 1e6:
        return f"{sign}${x/1e6:.1f}M"
    if x >= 1e3:
        return f"{sign}${x/1e3:.0f}K"
    return f"{sign}${x:.0f}"


# ---------------------------------------------------------------- real prices & fees
def taker_fee(price, rate):
    """Polymarket taker fee as a fraction of dollars staked.
    Fee = shares x rate x price x (1 - price); stake = shares x price; so fee/stake = rate x (1 - price)."""
    return rate * (1 - price)


def ask_quote(token_id, usd=100):
    """What buying costs right now, from the live order book.
    Returns {"ask": best ask, "fill": average price to buy `usd` worth, "filled_usd": $ actually
    available} or None if there is no book / nothing for sale."""
    if not token_id:
        return None
    body = get_json_raw("/book", {"token_id": token_id}, base=CLOB_API, retries=2)
    if not isinstance(body, dict):
        return None
    asks = sorted((num(a.get("price")), num(a.get("size"))) for a in body.get("asks") or []
                  if num(a.get("price")) > 0 and num(a.get("size")) > 0)
    if not asks:
        return None
    spent = shares = 0.0
    for p, size in asks:
        take = min(size, (usd - spent) / p)
        spent += take * p
        shares += take
        if spent >= usd - 1e-9:
            break
    return {"ask": asks[0][0], "fill": spent / shares, "filled_usd": spent}


FILL_FIELDS = ["alerted_at", "key", "checked_at", "secs_after", "mark", "ask", "fill_100",
               "filled_usd"]


def log_fill(path, key, alerted_at, alerted_ts, token_id, mark=""):
    """Append one order-book quote for an alert to the fills file (blank prices if no book)."""
    import csv
    q = ask_quote(token_id) or {}
    new_file = not os.path.exists(path)
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FILL_FIELDS)
        if new_file:
            w.writeheader()
        w.writerow({
            "alerted_at": alerted_at, "key": key,
            "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "secs_after": int(time.time() - alerted_ts), "mark": mark,
            "ask": round(q["ask"], 4) if q else "",
            "fill_100": round(q["fill"], 4) if q else "",
            "filled_usd": round(q["filled_usd"], 2) if q else "",
        })
    return q or None


def queue_recheck(state, key, alerted_at, token_id):
    """Remember an alert so a later scan can log what the price was a few minutes on."""
    if token_id:
        state.setdefault("recheck", []).append(
            {"key": key, "alerted_at": alerted_at, "ts": time.time(), "token": token_id})


def run_rechecks(state, path, min_age=120, max_age=1800):
    """Log a second quote for alerts sent at least `min_age` seconds ago (the price you'd
    realistically get after seeing the alert). Drops anything older than `max_age`."""
    keep, now = [], time.time()
    for r in state.get("recheck", []):
        age = now - r["ts"]
        if age < min_age:
            keep.append(r)
        elif age <= max_age:
            log_fill(path, r["key"], r["alerted_at"], r["ts"], r["token"])
    state["recheck"] = keep


# ---------------------------------------------------------------- sportsbook odds
# Optional: with an ODDS_API_KEY secret (free key from the-odds-api.com), each alert on a
# game market also records what DraftKings / FanDuel are offering for the same bet.
ODDS_API = "https://api.the-odds-api.com"
ODDS_BOOKS = os.environ.get("ODDS_BOOKS", "draftkings,fanduel")
ODDS_MIN_CREDITS = 25   # stop asking when the month's free quota is nearly used up
SPORT_KEYS = {"nba": "basketball_nba", "nfl": "americanfootball_nfl", "nhl": "icehockey_nhl",
              "mlb": "baseball_mlb", "cfb": "americanfootball_ncaaf", "cbb": "basketball_ncaab",
              "wnba": "basketball_wnba"}
BOOK_FIELDS = ["alerted_at", "key", "book", "decimal", "american", "implied"]
_odds_cache, _odds_left = {}, [None]


def _odds_events(sport, market):
    """Upcoming games with odds for one sport + bet type. One API credit, cached per run."""
    key = os.environ.get("ODDS_API_KEY")
    if not key:
        return []
    if (sport, market) in _odds_cache:
        return _odds_cache[(sport, market)]
    events = []
    if _odds_left[0] is None or _odds_left[0] >= ODDS_MIN_CREDITS:
        url = f"{ODDS_API}/v4/sports/{sport}/odds?" + urllib.parse.urlencode(
            {"apiKey": key, "bookmakers": ODDS_BOOKS, "markets": market, "oddsFormat": "decimal"})
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=20) as r:
                left = r.headers.get("x-requests-remaining")
                _odds_left[0] = int(float(left)) if left else None
                events = json.loads(r.read().decode())
        except Exception as e:  # noqa: BLE001  (never print the URL: it contains the key)
            print(f"  ! sportsbook odds lookup failed ({sport}/{market}): {type(e).__name__}",
                  file=sys.stderr)
    _odds_cache[(sport, market)] = events if isinstance(events, list) else []
    return _odds_cache[(sport, market)]


def _same_team(a, b):
    """'Celtics' matches 'Boston Celtics'; 'Nets' does not match 'Charlotte Hornets'."""
    a, b = (a or "").strip().lower(), (b or "").strip().lower()
    if not a or not b:
        return False
    return a == b or b.endswith(" " + a) or b.startswith(a + " ") \
        or a.endswith(" " + b) or a.startswith(b + " ")


def _bet_spec(title, outcome):
    """(bet type, line, team names) for a Polymarket game market, or None if it isn't one
    a sportsbook offers in the same form."""
    t = title or ""
    m = re.match(r"\s*Spread:\s*(.+?)\s*\(([-+]?\d+(?:\.\d+)?)\)", t)
    if m:
        fav, line = m.group(1), float(m.group(2))
        if _same_team(outcome, fav):
            return "spreads", line, [fav]
        return "spreads", -line, [fav, outcome]
    m = re.search(r"O/U\s*(\d+(?:\.\d+)?)", t)
    if m:
        teams = re.split(r"\s+vs\.?\s+", t.split(":")[0].strip())
        return ("totals", float(m.group(1)), teams) if len(teams) == 2 else None
    teams = re.split(r"\s+vs\.?\s+", t.strip())
    if len(teams) == 2 and ":" not in t and "?" not in t:
        return "h2h", None, teams
    return None


def american(decimal):
    return f"+{round((decimal - 1) * 100)}" if decimal >= 2 else f"-{round(100 / (decimal - 1))}"


def book_quote(title, outcome, slug, game_start=None):
    """Sportsbook prices for the same bet, best first:
    [{"book": "DraftKings", "decimal": 1.91}, ...]. Empty if no key, not a supported league,
    or the book's line isn't the same number (a -8.5 spread is not compared with -9)."""
    sport = SPORT_KEYS.get((slug or "").split("-")[0].lower())
    spec = _bet_spec(title, outcome)
    if not sport or not spec:
        return []
    market, point, teams = spec
    out = []
    for ev in _odds_events(sport, market):
        names = [ev.get("home_team") or "", ev.get("away_team") or ""]
        if not all(any(_same_team(t, n) for n in names) for t in teams):
            continue
        start = parse_time(ev.get("commence_time"))
        if game_start and start and abs(start - game_start) > 18 * 3600:
            continue
        for b in ev.get("bookmakers") or []:
            for mk in b.get("markets") or []:
                if mk.get("key") != market:
                    continue
                for o in mk.get("outcomes") or []:
                    name = o.get("name") or ""
                    hit = (name.lower() == (outcome or "").lower() if market == "totals"
                           else _same_team(outcome, name))
                    if hit and num(o.get("price")) > 1 and (
                            point is None or abs(num(o.get("point"), 1e9) - point) < 0.01):
                        out.append({"book": b.get("title") or b.get("key") or "?",
                                    "decimal": num(o.get("price"))})
        break
    return sorted(out, key=lambda q: -q["decimal"])


def log_books(path, key, alerted_at, quotes):
    """Append the sportsbook prices for one alert (nothing written if there are none)."""
    if not quotes:
        return
    import csv
    new_file = not os.path.exists(path)
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=BOOK_FIELDS)
        if new_file:
            w.writeheader()
        for q in quotes:
            w.writerow({"alerted_at": alerted_at, "key": key, "book": q["book"],
                        "decimal": round(q["decimal"], 3), "american": american(q["decimal"]),
                        "implied": round(1 / q["decimal"], 4)})
