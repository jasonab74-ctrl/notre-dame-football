# collect.py — fetch & filter, write items.json (ND football)
import feedparser, json, re, time, html
from datetime import datetime, timezone
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from feeds import FEEDS

MAX_ITEMS = 50

KEYWORDS_ANY = [
    "notre dame football", "fighting irish", "nd football",
    "marcus freeman", "south bend", "golden domers"
]
EXCLUDE_ANY = [
    "women", "wbb", "volleyball", "basketball", "softball",
    "baseball", "soccer", "lacrosse", "hockey"
]

# Sources that can bypass strict keyword checks
TRUSTED = {f["name"] for f in FEEDS}

def strip_tags(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()

def clean_url(u: str) -> str:
    try:
        p = urlparse(u)
        q = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True)
             if not k.lower().startswith(("utm_", "fbclid", "gclid", "ocid"))]
        return urlunparse((p.scheme, p.netloc, p.path, "", urlencode(q), ""))
    except Exception:
        return u

def allow_item(title: str, summary: str, source: str) -> bool:
    t = f"{title} {summary}".lower()
    if any(x in t for x in EXCLUDE_ANY):
        return False
    if source in TRUSTED:
        return True
    return any(k in t for k in KEYWORDS_ANY)

def ts_from_entry(e) -> float:
    for k in ("published_parsed", "updated_parsed"):
        if getattr(e, k, None):
            try:
                return time.mktime(getattr(e, k))
            except Exception:
                pass
    return time.time()

def make_id(link: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (link or "").lower()).strip("-")[:120]

def collect():
    items, seen = [], set()
    for feed in FEEDS:
        name, url = feed["name"], feed["url"]
        parsed = feedparser.parse(url)
        for e in parsed.entries:
            title = strip_tags(getattr(e, "title", ""))
            link  = clean_url(getattr(e, "link", ""))
            if not title or not link or (title, link) in seen:
                continue
            summary = strip_tags(getattr(e, "summary", ""))
            if not allow_item(title, summary, name):
                continue
            ts = ts_from_entry(e)
            items.append({
                "id": make_id(link),
                "title": title,
                "link": link,
                "source": name,
                "ts": ts,
                "published_iso": datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
            })
            seen.add((title, link))

    items.sort(key=lambda x: x["ts"], reverse=True)
    items = items[:MAX_ITEMS]

    with open("items.json", "w", encoding="utf-8") as f:
        json.dump({
            "updated_iso": datetime.now(tz=timezone.utc).isoformat(),
            "count": len(items),
            "items": items
        }, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    collect()