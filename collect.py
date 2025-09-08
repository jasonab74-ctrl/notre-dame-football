#!/usr/bin/env python3
# Notre Dame Football — hardened collector
# - Curated, stable source list for dropdown
# - Strict filters (football-only)
# - Always writes updated timestamp & buttons

import json, time, re, hashlib
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from datetime import datetime, timezone
import feedparser
from feeds import FEEDS, STATIC_LINKS

MAX_ITEMS = 60

# ---- Curated dropdown (10 good ND football sources) ----
CURATED_SOURCES = [
    "UND.com",
    "ND Insider (SBT)",
    "One Foot Down",
    "Blue & Gold (On3)",
    "Inside ND Sports (Rivals)",
    "247Sports ND",
    "Fighting Irish Wire",
    "The Athletic",
    "ESPN",
    "CBS Sports",
]
ALLOWED_SOURCES = set(CURATED_SOURCES)

# ---- utils ----
def now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

def _host(u: str) -> str:
    try:
        n = urlparse(u).netloc.lower()
        for p in ("www.","m.","amp."):
            if n.startswith(p): n = n[len(p):]
        return n
    except Exception:
        return ""

def canonical(u: str) -> str:
    try:
        p = urlparse(u)
        keep = {"id","story","v","p"}
        q = parse_qs(p.query)
        q = {k:v for k,v in q.items() if k in keep}
        p = p._replace(query=urlencode(q, doseq=True), fragment="", netloc=_host(u))
        return urlunparse(p)
    except Exception:
        return u

def hid(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:16]

ALIASES = {
    "und.com":                  "UND.com",
    "ndinsider.com":            "ND Insider (SBT)",
    "onefootdown.com":          "One Foot Down",
    "on3.com":                  "Blue & Gold (On3)",
    "rivals.com":               "Inside ND Sports (Rivals)",
    "247sports.com":            "247Sports ND",
    "irishwire.usatoday.com":   "Fighting Irish Wire",
    "theathletic.com":          "The Athletic",
    "espn.com":                 "ESPN",
    "cbssports.com":            "CBS Sports",
    # normalize common amp hosts by canonical()
}

# ---- content filters ----
KEEP = [
    r"\bNotre Dame\b",
    r"\bFighting Irish\b",
    r"\bIrish\b",
    r"\bND\b",
    r"\bMarcus Freeman\b",
    r"\bSouth Bend\b",
]
FOOTBALL = [
    r"\bfootball\b", r"\bCFB\b", r"\bcollege football\b", r"\bNCAA\b"
]
DROP = [
    r"\bwomen'?s\b", r"\bWBB\b", r"\bbasketball\b", r"\bbaseball\b", r"\bsoftball\b",
    r"\bsoccer\b", r"\bhockey\b", r"\bvolleyball\b", r"\bgolf\b", r"\btrack\b",
]

def text_ok(title: str, summary: str) -> bool:
    t = f"{title} {summary}"
    if any(re.search(p, t, re.I) for p in DROP): return False
    if not any(re.search(p, t, re.I) for p in KEEP): return False
    if not any(re.search(p, t, re.I) for p in FOOTBALL): return False
    return True

def parse_time(entry):
    for key in ("published_parsed","updated_parsed"):
        if entry.get(key):
            try:
                return time.strftime("%Y-%m-%dT%H:%M:%S%z", entry[key])
            except Exception:
                pass
    return now_iso()

def source_label(link: str, feed_name: str) -> str:
    return ALIASES.get(_host(link), feed_name.strip())

# ---- pipeline ----
def fetch_all():
    items, seen = [], set()
    for f in FEEDS:
        fname, furl = f["name"].strip(), f["url"].strip()
        try:
            parsed = feedparser.parse(furl)
        except Exception:
            continue
        for e in parsed.entries[:120]:
            link = canonical((e.get("link") or e.get("id") or "").strip())
            if not link: continue
            key = hid(link)
            if key in seen: continue

            src = source_label(link, fname)
            if src not in ALLOWED_SOURCES:
                continue  # keeps dropdown clean/curated

            title = (e.get("title") or "").strip()
            summary = (e.get("summary") or e.get("description") or "").strip()
            if not text_ok(title, summary): continue

            items.append({
                "id": key,
                "title": title or "(untitled)",
                "link": link,
                "source": src,
                "feed": fname,
                "published": parse_time(e),
                "summary": summary,
            })
            seen.add(key)

    items.sort(key=lambda x: x["published"], reverse=True)
    return items[:MAX_ITEMS]

def write_items(items):
    payload = {
        "updated": now_iso(),
        "items": items,
        "links": STATIC_LINKS,        # buttons always shown
        "sources": CURATED_SOURCES,   # dropdown never collapses
    }
    with open("items.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

def main():
    write_items(fetch_all())

if __name__ == "__main__":
    main()
