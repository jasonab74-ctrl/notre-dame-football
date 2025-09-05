# collect.py — fetch + filter feeds, write items.json (cap 50)
import json, time, hashlib
from datetime import datetime, timezone
import feedparser
from urllib.parse import urlparse

from feeds import FEEDS

# Tweakable settings
MAX_ITEMS = 50
TRUSTED_SOURCES = {
    "One Foot Down",
    "Blue & Gold — On3 Notre Dame",
    "247Sports — Notre Dame",
    "Official — UND.com Football (via Google)",
    "ESPN — Notre Dame (via Google)",
}

INCLUDE_TOKENS = [
    "notre dame", "fighting irish", "south bend",
    "football", "ndfb", "freeman", "marcus freeman"
]
EXCLUDE_TOKENS = [
    # hard filters for other sports/noise
    "basketball", "mbb", "wbb", "women", "softball", "baseball",
    "volleyball", "soccer", "hockey", "lacrosse", "golf",
]

def norm(s: str) -> str:
    return (s or "").lower()

def host_of(url: str) -> str:
    try:
        return urlparse(url).netloc
    except Exception:
        return ""

def allow_item(item, feed_name: str) -> bool:
    title = norm(item.get("title"))
    summary = norm(item.get("summary"))
    text = f"{title} {summary}"

    # Trusted sources pass unless explicitly excluded
    if feed_name in TRUSTED_SOURCES:
        for bad in EXCLUDE_TOKENS:
            if bad in text:
                return False
        # If it mentions Notre Dame or Irish at all, pass
        if "notre dame" in text or "fighting irish" in text or "nd" in text:
            return True

    # Strict filter: needs BOTH a team mention and football context
    team_hit = any(tok in text for tok in ["notre dame", "fighting irish", "south bend"])
    football_hit = any(tok in text for tok in ["football", "ndfb"])
    if team_hit and football_hit:
        # make sure it isn't obviously another sport
        for bad in EXCLUDE_TOKENS:
            if bad in text:
                return False
        return True
    return False

def uniq_key(link: str, title: str) -> str:
    raw = (link or "") + "|" + (title or "")
    return hashlib.md5(raw.encode("utf-8")).hexdigest()

def parse_time(entry):
    # Prefer published_parsed; fall back to now
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
            source = name
            domain = host_of(link)

            key = uniq_key(link, title)
            if key in items_by_key:
                # prefer earliest discovered time consistency — keep first or update older/newer?
                # We'll keep the earliest (do nothing)
                continue

            items_by_key[key] = {
                "title": title,
                "link": link,
                "summary": summary,
                "published": published_ts,
                "source": source,
                "domain": domain,
            }

    # Sort newest first, cap to MAX_ITEMS
    items = sorted(items_by_key.values(), key=lambda x: x["published"], reverse=True)[:MAX_ITEMS]

    payload = {
        "team": "Notre Dame Fighting Irish — Football",
        "updated": int(time.time()),
        "count": len(items),
        "items": items
    }
    with open("items.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(items)} items to items.json at {datetime.now(timezone.utc).isoformat()}")

if __name__ == "__main__":
    collect()
