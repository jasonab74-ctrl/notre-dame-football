# collect.py — fetch & filter ND football, dedupe, label by real outlet, write items.json
import feedparser, json, re, time, html
from datetime import datetime, timezone
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from feeds import FEEDS

MAX_ITEMS = 50

# Require football context; allow common ND terms and key people
KEYWORDS_ANY = [
    "notre dame football", "nd football", "fighting irish",
    "marcus freeman", "golden domers", "south bend", "irish football",
    "freeman", "notre dame vs", "notre dame at", "nd vs", "nd at"
]
# Must include at least one of these football hints if the feed is an aggregator
FOOTBALL_HINTS = ["football", "ncaa", "ncaaf", "ncf", "qb", "defense", "offense", "linebacker", "wide receiver", "running back"]

EXCLUDE_ANY = [
    "women", "wbb", "volleyball", "basketball", "softball",
    "baseball", "soccer", "lacrosse", "hockey", "wrestling"
]

# Pretty outlet names for common domains
DOMAIN_LABELS = {
    "espn.com": "ESPN",
    "cbssports.com": "CBS Sports",
    "247sports.com": "247Sports",
    "blueandgold.com": "Blue & Gold (On3)",
    "on3.com": "On3",
    "southbendtribune.com": "South Bend Tribune",
    "usatoday.com": "USA Today",
    "fightingirishwire.usatoday.com": "Fighting Irish Wire",
    "si.com": "Sports Illustrated",
    "sports.yahoo.com": "Yahoo Sports",
    "yahoo.com": "Yahoo",
    "nbcsports.com": "NBC Sports",
    "foxsports.com": "FOX Sports",
    "onefootdown.com": "One Foot Down",
    "fightingirish.com": "FightingIrish.com",
    "notredame.rivals.com": "Inside ND Sports (Rivals)",
    "insideindsports.com": "Inside ND Sports",
    "wndu.com": "WNDU",
    "theathletic.com": "The Athletic",
    "apnews.com": "AP News",
    "bleacherreport.com": "Bleacher Report",
    "reddit.com": "Reddit",
}

AGGREGATOR_HOSTS = {"news.google.com", "www.bing.com", "bing.com"}

def strip_tags(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()

def unwrap_redirect(u: str) -> str:
    """Unwrap Google/Bing news redirectors to the real article URL when present."""
    try:
        p = urlparse(u)
        q = dict(parse_qsl(p.query, keep_blank_values=True))
        if p.netloc in {"news.google.com"} and "url" in q:
            return q["url"]
        if p.netloc in {"www.bing.com", "bing.com"} and "url" in q:
            return q["url"]
        return u
    except Exception:
        return u

def clean_url(u: str) -> str:
    """Canonicalize and drop tracking params from the final URL."""
    try:
        u = unwrap_redirect(u)
        p = urlparse(u)
        q_pairs = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True)
                   if not k.lower().startswith(("utm_", "fbclid", "gclid", "ocid"))]
        return urlunparse((p.scheme, p.netloc.lower(), p.path, "", urlencode(q_pairs), ""))
    except Exception:
        return u

def outlet_label_from_url(u: str) -> str:
    try:
        host = urlparse(u).netloc.lower()
        host = host[4:] if host.startswith("www.") else host
        return DOMAIN_LABELS.get(host, host)
    except Exception:
        return "Unknown"

def looks_like_football(text: str) -> bool:
    t = text.lower()
    if "football" in t:
        return True
    return any(k in t for k in FOOTBALL_HINTS)

def allow_item(title: str, summary: str, link: str, feed_host: str) -> bool:
    """Stricter filter for aggregator feeds: require ND + football context."""
    t = f"{title} {summary}".lower()
    if any(x in t for x in EXCLUDE_ANY):
        return False
    # Must be ND-related
    if not any(k in t for k in KEYWORDS_ANY):
        return False
    # If aggregator, also require an explicit football-ish hint
    if feed_host in AGGREGATOR_HOSTS and not looks_like_football(t):
        return False
    return True

def ts_from_entry(e) -> float:
    for k in ("published_parsed", "updated_parsed"):
        v = getattr(e, k, None)
        if v:
            try:
                return time.mktime(v)
            except Exception:
                pass
    return time.time()

def make_id(link: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (link or "").lower()).strip("-")[:120]

def norm_title(t: str) -> str:
    t = t.lower()
    t = re.sub(r"[^a-z0-9 ]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    # drop trailing site separators like " - on3" that slip into some titles
    t = re.sub(r"\s-\s[a-z0-9 ]+$", "", t)
    return t

def collect():
    items = []
    seen_links = set()             # canonical link dedupe
    seen_title_key = set()         # domain+norm_title dedupe

    for feed in FEEDS:
        feed_name, feed_url = feed["name"], feed["url"]
        feed_host = urlparse(feed_url).netloc.lower()
        parsed = feedparser.parse(feed_url)

        for e in parsed.entries:
            raw_title = getattr(e, "title", "") or ""
            title = strip_tags(raw_title)
            raw_link = getattr(e, "link", "") or ""
            link = clean_url(raw_link)
            if not title or not link:
                continue

            # stricter allowlist
            summary = strip_tags(getattr(e, "summary", ""))
            if not allow_item(title, summary, link, feed_host):
                continue

            # dedupe: canonical link
            if link in seen_links:
                continue

            # dedupe: per-domain normalized title
            domain = urlparse(link).netloc.lower()
            domain = domain[4:] if domain.startswith("www.") else domain
            title_key = f"{domain}::{norm_title(title)}"
            if title_key in seen_title_key:
                continue

            ts = ts_from_entry(e)
            source = outlet_label_from_url(link)

            items.append({
                "id": make_id(link),
                "title": title,
                "link": link,
                "source": source,                          # used in dropdown
                "ts": float(ts),                           # epoch seconds
                "published_iso": datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
            })

            seen_links.add(link)
            seen_title_key.add(title_key)

    # newest first + cap
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