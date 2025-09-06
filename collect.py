# collect.py — fetch ND football news, unwrap aggregator links, dedupe, label by real outlet
import feedparser, json, re, time, html
from datetime import datetime, timezone
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from feeds import FEEDS

MAX_ITEMS = 50

# ND + football context
KEYWORDS_ANY = [
    "notre dame football", "nd football", "fighting irish",
    "marcus freeman", "irish football", "south bend",
    "notre dame vs", "notre dame at", "nd vs", "nd at"
]
FOOTBALL_HINTS = [
    "football", "ncaaf", "ncf", "qb", "quarterback", "defense", "offense",
    "linebacker", "receiver", "running back", "depth chart", "bye week"
]
EXCLUDE_ANY = [
    "women", "wbb", "volleyball", "basketball", "softball", "baseball",
    "soccer", "lacrosse", "hockey", "wrestling"
]

AGGREGATOR_HOSTS = {"news.google.com", "www.bing.com", "bing.com"}

DOMAIN_LABELS = {
    "espn.com": "ESPN",
    "cbssports.com": "CBS Sports",
    "247sports.com": "247Sports",
    "blueandgold.com": "Blue & Gold (On3)",
    "on3.com": "On3",
    "southbendtribune.com": "South Bend Tribune",
    "fightingirishwire.usatoday.com": "Fighting Irish Wire",
    "usatoday.com": "USA Today",
    "si.com": "Sports Illustrated",
    "sports.yahoo.com": "Yahoo Sports",
    "yahoo.com": "Yahoo",
    "nbcsports.com": "NBC Sports",
    "foxsports.com": "FOX Sports",
    "onefootdown.com": "One Foot Down",
    "fightingirish.com": "FightingIrish.com",
    "insideindsports.com": "Inside ND Sports",
    "notredame.rivals.com": "Inside ND Sports (Rivals)",
    "wndu.com": "WNDU",
    "theathletic.com": "The Athletic",
    "apnews.com": "AP News",
    "bleacherreport.com": "Bleacher Report",
    "reddit.com": "Reddit",
}

def strip_tags(s: str) -> str:
    if not s: return ""
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()

def unwrap_redirect(u: str) -> str:
    """Unwrap Google/Bing news links to the real article when possible."""
    try:
        p = urlparse(u)
        q = dict(parse_qsl(p.query, keep_blank_values=True))
        if p.netloc == "news.google.com" and "url" in q:
            return q["url"]
        if p.netloc in {"www.bing.com", "bing.com"}:
            # Bing uses url= or u=
            if "url" in q: return q["url"]
            if "u" in q:   return q["u"]
        return u
    except Exception:
        return u

def clean_url(u: str) -> str:
    """Canonicalize final URL and drop tracking."""
    try:
        u = unwrap_redirect(u)
        p = urlparse(u)
        q = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True)
             if not k.lower().startswith(("utm_", "fbclid", "gclid", "ocid"))]
        host = (p.netloc or "").lower()
        if host.startswith("www."): host = host[4:]
        return urlunparse((p.scheme, host, p.path, "", urlencode(q), ""))
    except Exception:
        return u

def outlet_label(u: str, entry, default_feed_name: str) -> str:
    """Prefer real outlet (domain). If still an aggregator, fall back to <source> tag."""
    try:
        host = urlparse(u).netloc.lower()
        if host.startswith("www."): host = host[4:]
        if host and host not in AGGREGATOR_HOSTS:
            return DOMAIN_LABELS.get(host, host)
        # Fall back to <source> / source_detail from the feed (Google News provides this)
        src = entry.get("source") or entry.get("source_detail") or {}
        if isinstance(src, dict):
            title = src.get("title") or src.get("href")
            if title:
                # If it's a URL, map to domain label
                if "://" in title:
                    try:
                        h = urlparse(title).netloc.lower()
                        if h.startswith("www."): h = h[4:]
                        return DOMAIN_LABELS.get(h, h or default_feed_name)
                    except Exception:
                        pass
                return title
        return default_feed_name
    except Exception:
        return default_feed_name

def looks_like_football(text: str) -> bool:
    t = text.lower()
    if "football" in t: return True
    return any(k in t for k in FOOTBALL_HINTS)

def allowed(title: str, summary: str, feed_host: str) -> bool:
    t = f"{title} {summary}".lower()
    if any(x in t for x in EXCLUDE_ANY): return False
    if not any(k in t for k in KEYWORDS_ANY): return False
    if feed_host in AGGREGATOR_HOSTS and not looks_like_football(t): return False
    return True

def ts_from_entry(e) -> float:
    for k in ("published_parsed", "updated_parsed"):
        v = getattr(e, k, None)
        if v:
            try: return time.mktime(v)
            except Exception: pass
    return time.time()

def norm_title(t: str) -> str:
    t = t.lower()
    t = re.sub(r"[^a-z0-9 ]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(r"\s-\s[a-z0-9 ]+$", "", t)  # drop trailing " - Site"
    return t

def make_id(link: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (link or "").lower()).strip("-")[:120]

def collect():
    items = []
    seen_links = set()          # canonical URL dedupe
    seen_titles = set()         # global normalized title dedupe

    for feed in FEEDS:
        feed_name = feed["name"]
        feed_url  = feed["url"]
        feed_host = urlparse(feed_url).netloc.lower()

        parsed = feedparser.parse(feed_url)
        for e in parsed.entries:
            title = strip_tags(getattr(e, "title", "") or "")
            link  = clean_url(getattr(e, "link", "") or "")
            if not title or not link: 
                continue

            summary = strip_tags(getattr(e, "summary", "") or "")
            if not allowed(title, summary, feed_host):
                continue

            # DEDUPE 1: by canonical URL
            if link in seen_links:
                continue

            # DEDUPE 2: by normalized title across ALL outlets
            key = norm_title(title)
            if key in seen_titles:
                continue

            ts = ts_from_entry(e)
            source = outlet_label(link, e, feed_name)

            items.append({
                "id": make_id(link),
                "title": title,
                "link": link,
                "source": source,                    # used in dropdown
                "ts": float(ts),
                "published_iso": datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
            })
            seen_links.add(link)
            seen_titles.add(key)

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