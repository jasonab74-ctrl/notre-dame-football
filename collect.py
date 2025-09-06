# collect.py — fetch + filter ND football, dedupe, write items.json
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

TRUSTED = {f["name"] for f in FEEDS}  # allow all defined feeds

def strip_tags(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()

def clean_url(u: str) -> str:
    # Canonicalize and drop tracking params
    try:
        p = urlparse(u)
        # If Google News wrapper, unwrap to the real article URL when present
        q_all = dict(parse_qsl(p.query, keep_blank_values=True))
        if "news.google.com" in p.netloc and "url" in q_all:
            u = q_all["url"]
            p = urlparse(u)
            q_all = dict(parse_qsl(p.query, keep_blank_values=True))
        q = [(k, v) for k, v in q_all.items()
             if not k.lower().startswith(("utm_", "fbclid", "gclid", "ocid"))]
        return urlunparse((p.scheme, p.netloc, p.path, "", urlencode(q), ""))
    except Exception:
        return u

def allow_item(title: str, summary: str, source_feed_name: str) -> bool:
    t = f"{title} {summary}".lower()
    if any(x in t for x in EXCLUDE_ANY):
        return False
    if source_feed_name in TRUSTED:
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

def entry_outlet(e, default_feed_name: str) -> str:
    # Prefer the underlying outlet for aggregator feeds (Google/Bing News).
    try:
        src = e.get("source")  # FeedParserDict or None
        if isinstance(src, dict):
            return src.get("title") or src.get("href") or default_feed_name
    except Exception:
        pass
    # Some feeds use source_detail
    try:
        sd = e.get("source_detail")
        if isinstance(sd, dict):
            return sd.get("title") or sd.get("href") or default_feed_name
    except Exception:
        pass
    return default_feed_name

def make_id(link: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (link or "").lower()).strip("-")[:120]

def collect():
    items, seen_links = [], set()
    for feed in FEEDS:
        name, url = feed["name"], feed["url"]
        parsed = feedparser.parse(url)
        for e in parsed.entries:
            title = strip_tags(getattr(e, "title", ""))
            link  = clean_url(getattr(e, "link", ""))
            if not title or not link:
                continue
            if link in seen_links:
                continue

            summary = strip_tags(getattr(e, "summary", ""))
            if not allow_item(title, summary, name):
                continue

            ts = ts_from_entry(e)
            outlet = entry_outlet(e, name)

            items.append({
                "id": make_id(link),
                "title": title,
                "link": link,
                "source": outlet,                 # <-- outlet for dropdown richness
                "feed": name,                     # original feed name (for debugging)
                "ts": float(ts),                  # epoch seconds
                "published_iso": datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
            })
            seen_links.add(link)

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