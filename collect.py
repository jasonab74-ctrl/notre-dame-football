# collect.py — resilient feed collector for Notre Dame Football
# Never exits non-zero; always writes items.json even if feeds fail.

import json, time, hashlib, traceback
from datetime import datetime, timezone
from urllib.parse import urlparse

import feedparser

from feeds import FEEDS

MAX_ITEMS = 50

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

    if feed_name in TRUSTED_SOURCES:
        if any(tok in text for tok in TEAM_TOKENS) or "notre" in text or "irish" in text:
            return True
        return "notre" in norm(feed_name) or "irish" in norm(feed_name)

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
    errors = []

    for f in FEEDS:
        name = f.get("name", "Unknown")
        url = f.get("url")
        if not url:
            continue

        try:
            d = feedparser.parse(url)
            # feedparser never raises for bad feeds; it sets bozo flag.
            if getattr(d, "bozo", False):
                print(f"[WARN] BOZO feed: {name} — {getattr(d, 'bozo_exception', '')}")

            for e in d.entries:
                title = e.get("title", "").strip()
                link = e.get("link", "").strip()
                if not title or not link:
                    continue
                if not allow_item(e, name):
                    continue

                key = uniq_key(link, title)
                if key in items_by_key:
                    continue

                items_by_key[key] = {
                    "title": title,
                    "link": link,
                    "summary": e.get("summary", "") or e.get("description", ""),
                    "published": parse_time(e),
                    "source": name,
                    "domain": host_of(link),
                }

            print(f"[OK] {name}: {len(getattr(d, 'entries', []))} entries parsed")

        except Exception as ex:
            msg = f"[ERROR] {name}: {ex}"
            errors.append(msg)
            print(msg)
            traceback.print_exc()

    items = sorted(items_by_key.values(), key=lambda x: x["published"], reverse=True)[:MAX_ITEMS]
    payload = {
        "team": "Notre Dame Football",
        "updated": int(time.time()),
        "count": len(items),
        "items": items,
        "notes": {"errors": errors[:10]}  # keep a peek at problems without failing
    }

    with open("items.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    ts = datetime.now(timezone.utc).isoformat()
    print(f"[WRITE] items.json — {len(items)} items @ {ts} (UTC)")
    if errors:
        print(f"[INFO] Non-fatal feed errors: {len(errors)} (written into items.json.notes)")

if __name__ == "__main__":
    # Never raise — we always write a valid items.json and exit(0)
    try:
        collect()
    except Exception as e:
        print(f"[FATAL] collector crashed unexpectedly: {e}")
        traceback.print_exc()
        # write a minimal file so the site still renders
        with open("items.json", "w", encoding="utf-8") as f:
            json.dump({"team":"Notre Dame Football","updated":int(time.time()),"count":0,"items":[]}, f, indent=2)
        # do NOT exit non-zero — GH Actions will mark job green
