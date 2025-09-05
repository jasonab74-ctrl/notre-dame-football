# collect.py — fetch + filter feeds, write items.json (cap 50)
import json, time, hashlib
from datetime import datetime, timezone
import feedparser
from urllib.parse import urlparse

from feeds import FEEDS

MAX_ITEMS = 50

# Safe sources: pass unless clearly another sport
TRUSTED_SOURCES = {
    "UND.com — News (via Google)",
    "South Bend Tribune — ND Insider (via Google)",
    "Chicago Tribune — Notre Dame (via Google)",
    "NBC Sports — Notre Dame",
    "CBS Sports — Notre Dame (via Google)",
    "Yahoo Sports — Notre Dame (via Google)",
    "USA Today — Fighting Irish Wire (via Google)",
    "The Athletic — Notre Dame (via Google)",
    "One Foot Down (SB Nation)",
    "Blue & Gold — On3",
    "247Sports — Notre Dame",
    "Irish Illustrated (Rivals via Google)",
    "ESPN — Notre Dame (via Google)",
    "AP News — Notre Dame (via Google)",
}

# Exclude obvious other sports
EXCLUDE_TOKENS = [
    "basketball", "mbb", "wbb", "women", "softball", "baseball",
    "volleyball", "soccer", "hockey", "lacrosse", "golf", "tennis",
]

TEAM_TOKENS = ["notre dame", "fighting irish", "south bend", " nd "]
FOOTBALL_HINTS = ["football", "ndfb", "marcus freeman", "qb", "quarterback", "linebacker"]

def norm(s: str) -> str:
    return (s or "").lower()

def host_of(url: str) -> str:
    try:
        return urlparse(url).netloc
    except Exception:
        return ""

def allow_item(entry, feed_name: str) -> bool:
    title = norm(entry.get("title"))
    summary = norm(entry.get("summary") or entry.get("description") or "")
    text = f"{title} {summary}"

    for bad in EXCLUDE_TOKENS:
        if bad in text:
            return False

    # Trusted sources: allow with team hint
    if feed_name in TRUSTED_SOURCES:
        if any(tok in text for tok in TEAM_TOKENS) or "notre" in text or "irish" in text:
            return True
        return "notre" in norm(feed_name) or "irish" in norm(feed_name)

    # Others: require team + football-ish
    team_hit = any(tok in text for tok in TEAM_TOKENS) or "notre" in text
    footballish = "football" in text or any(tok in text for tok in FOOTBALL_HINTS)
    return team_hit and footballish

def uniq_key(link: str, title: str) -> str:
    raw = (link or "") + "|" + (title or "")
    return hashlib.md5(raw.encode("utf-8")).hexdigest()

def parse_time(entry):
    try:
        if getattr(entry, "published_parsed", None):
            return int(time.mktime(entry.published_parsed))
        if getattr(entry, "updated_parsed", None):
            return int(time.mktime(entry.updated_parsed))
    except Exception:
        pass
    return int(time.time())

def collect():
    items_by_key = {}
    for f in FEEDS:
        name = f["name"]
        url = f["url"]
        d = feedparser.parse(url)

        for e in d.entries:
            title = e.get("title", "").strip()
            link = e.get("link", "").strip()
            if not title or not link:
                continue
            if not allow_item(e, name):
                continue

            published_ts = parse_time(e)
            summary = e.get("summary", "") or e.get("description", "")
            domain = host_of(link)

            key = uniq_key(link, title)
            if key in items_by_key:
                continue

            items_by_key[key] = {
                "title": title,
                "link": link,
                "summary": summary,
                "published": published_ts,
                "source": name,
                "domain": domain,
            }

    items = sorted(items_by_key.values(), key=lambda x: x["published"], reverse=True)[:MAX_ITEMS]
    payload = {
        "team": "Notre Dame Football",
        "updated": int(time.time()),
        "count": len(items),
        "items": items
    }
    with open("items.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(items)} items to items.json at {datetime.now(timezone.utc).isoformat()}")

if __name__ == "__main__":
    collect()
