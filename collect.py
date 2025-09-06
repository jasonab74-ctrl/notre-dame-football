# collect.py — ND Football collector with robust outlet extraction + hard dedupe
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
    "football", "ncaaf", "ncf", "qb", "quarterback",
    "defense", "offense", "linebacker", "receiver", "running back",
    "depth chart", "bye week"
]
EXCLUDE_ANY = [
    "women", "wbb", "volleyball", "basketball", "softball",
    "baseball", "soccer", "lacrosse", "hockey", "wrestling"
]

AGGREGATORS = {"news.google.com", "www.bing.com", "bing.com"}

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

# ---------------- helpers

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
            return q.get("url") or q.get("u") or u
        return u
    except Exception:
        return u

def clean_url(u: str) -> str:
    """Canonicalize final URL and drop tracking params."""
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

# Robust outlet-in-title extractor: accepts -, – or — with flexible spaces.
DASH = r"[-–—]"
OUTLET_RE = re.compile(rf"\s{DASH}\s([A-Za-z0-9&@.,'()/:+ ]+?)\s*$")

def split_title_outlet(title: str):
    """
    Parse 'Headline - Outlet' / 'Headline – Outlet' / 'Headline — Outlet'
    and return (clean_title, outlet). If no suffix, outlet=None.
    """
    m = OUTLET_RE.search(title)
    if not m:
        return title, None
    outlet = m.group(1).strip()
    # Avoid catching trivial stubs
    if len(outlet) < 2:
        return title, None
    clean = title[:m.start()].rstrip()
    return clean, outlet

def outlet_from_url(u: str, default_feed_name: str) -> str:
    try:
        host = urlparse(u).netloc.lower()
        if host.startswith("www."): host = host[4:]
        if host and host not in AGGREGATORS:
            return DOMAIN_LABELS.get(host, host)
        return default_feed_name
    except Exception:
        return default_feed_name

def entry_source_title(entry) -> str | None:
    """Pull <source> or source_detail title if present (Google News provides this)."""
    try:
        src = getattr(entry, "source", None)
        if isinstance(src, dict):
            t = src.get("title") or src.get("href")
            if t: return t
    except Exception:
        pass
    try:
        sd = getattr(entry, "source_detail", None)
        if isinstance(sd, dict):
            t = sd.get("title") or sd.get("href")
            if t: return t
    except Exception:
        pass
    return None

def looks_like_football(text: str) -> bool:
    t = text.lower()
    if "football" in t: return True
    return any(k in t for k in FOOTBALL_HINTS)

def allowed(title: str, summary: str, feed_host: str) -> bool:
    t = f"{title} {summary}".lower()
    if any(x in t for x in EXCLUDE_ANY): return False
    if not any(k in t for k in KEYWORDS_ANY): return False
    if feed_host in AGGREGATORS and not looks_like_football(t): return False
    return True

def ts_from_entry(e) -> float:
    for k in ("published_parsed", "updated_parsed"):
        v = getattr(e, k, None)
        if v:
            try: return time.mktime(v)
            except Exception: pass
    return time.time()

def norm_title(t: str) -> str:
    # normalize dashes; remove any trailing " - Outlet" piece; strip symbols; collapse space
    t = t.lower()
    t = re.sub(r"[–—]", "-", t)
    t = re.sub(rf"\s-\s[a-z0-9&@.,'()/:+ ]+$", "", t)
    t = re.sub(r"[^a-z0-9 ]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def make_id(link: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (link or "").lower()).strip("-")[:120]

# ---------------- main

def collect():
    items = []
    seen_links = set()   # canonical URL dedupe
    seen_titles = set()  # global normalized-title dedupe

    for feed in FEEDS:
        feed_name = feed["name"]
        feed_url  = feed["url"]
        feed_host = urlparse(feed_url).netloc.lower()

        parsed = feedparser.parse(feed_url)
        for e in parsed.entries:
            raw_title = getattr(e, "title", "") or ""
            title = strip_tags(raw_title)
            link  = clean_url(getattr(e, "link", "") or "")
            if not title or not link:
                continue

            summary = strip_tags(getattr(e, "summary", "") or "")
            if not allowed(title, summary, feed_host):
                continue

            # Dedup 1: canonical URL
            if link in seen_links:
                continue

            # Pull outlet from title; if missing, try <source>; then final URL.
            title_no_suffix, outlet_from_title = split_title_outlet(title)
            base_title = title_no_suffix or title

            source_from_tag = entry_source_title(e)
            if source_from_tag and "google" not in source_from_tag.lower():
                source_guess = source_from_tag
            else:
                source_guess = outlet_from_title or outlet_from_url(link, feed_name)

            # Dedup 2: global normalized title (after removing outlet suffix)
            title_key = norm_title(base_title)
            if title_key in seen_titles:
                continue

            ts = ts_from_entry(e)

            items.append({
                "id": make_id(link),
                "title": base_title,
                "link": link,
                "source": source_guess,                    # drives dropdown
                "ts": float(ts),
                "published_iso": datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
            })

            seen_links.add(link)
            seen_titles.add(title_key)

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