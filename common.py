"""Shared helpers for PolyTail: Polymarket API calls, market resolutions, Telegram."""

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

DATA_API = "https://data-api.polymarket.com"
GAMMA_API = "https://gamma-api.polymarket.com"
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
