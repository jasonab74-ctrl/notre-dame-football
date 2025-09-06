# collect.py — robust feed collector for Sports App (Notre Dame Football)
#
# Usage (default writes ./items.json):
#   python3 collect.py
#
# Optional:
#   python3 collect.py --out static/teams/notre-dame/items.json
#
# Notes:
# - Reads FEEDS from feeds.py (list of {name, url} or just {name} for labels).
# - Never crashes on a single bad feed; logs and continues.
# - Filters to Notre Dame Football content; trusted domains bypass strict filter.
# - Caps to MAX_ITEMS and writes schema your server expects.

import argparse
import json
import sys
import time
import traceback
import re
from urllib.parse import urlparse

import feedparser

APP_TITLE = "Notre Dame Football"
MAX_ITEMS = 50

# ---------- Filtering configuration ----------

RE_REQUIRED_ANY = [
    r"\bnotre\s*dame\b",
    r"\bnd\b",  # sometimes abbreviated
    r"\bfighting\s*irish\b",
]

RE_REQUIRED_SPORT = [
    r"\bfootball\b",
    r"\bCFB\b",
]

RE_EXCLUDE = [
    r"\bwomen'?s\b",
    r"\bwbb\b",
    r"\bvolleyball\b",
    r"\bbasketball\b",   # exclude hoops for this site
    r"\bbaseball\b",
    r"\bsoftball\b",
    r"\bsoccer\b",
]

TRUSTED_DOMAINS = {
    "und.com",
    "onefootdown.com",
    "slapthesign.com",
    "ndinsider.com",
    "ndnation.com",
    "irishsportsdaily.com",
    "insideindsports.com",  # rivals
    "247sports.com",
    "cbssports.com",
    "espn.com",
    "on3.com",
    "theathletic.com",
    "usatoday.com",  # fightingirishwire.usatoday.com
    "fightingirishwire.usatoday.com",
    "youtube.com",
    "www.youtube.com",
}

TITLE_LEN_MIN = 20  # ignore super tiny “noise” items


def log(msg: str):
    print(f"[collect] {msg}", flush=True)


def load_feeds():
    """Import FEEDS from feeds.py; tolerate missing/invalid."""
    try:
        from feeds import FEEDS  # type: ignore
    except Exception as e:
        log(f"feeds import failed: {e}")
        return []
    # Normalize: keep only items with url when present; name optional for label
    norm = []
    for f in FEEDS:
        # Some configs may be label-only (for dropdown). Skip those here.
        url = f.get("url")
        if url:
            norm.append({"name": f.get("name") or url, "url": url})
    if not norm:
        log("No feed URLs found in feeds.py FEEDS — using an empty list.")
    return norm


def strip_html(text: str) -> str:
    if not text:
        return ""
    # remove tags
    text = re.sub(r"<[^>]+>", " ", text)
    # collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def choose_epoch(entry) -> int:
    for k in ("published_parsed", "updated_parsed", "created_parsed"):
        val = entry.get(k)
        if val:
            try:
                return int(time.mktime(val))
            except Exception:
                pass
    return int(time.time())


def hostname(url: str) -> str:
    try:
        return urlparse(url).hostname or ""
    except Exception:
        return ""


def is_trusted(url: str) -> bool:
    host = hostname(url).lower()
    if not host:
        return False
    # allow subdomains
    for td in TRUSTED_DOMAINS:
        if host == td or host.endswith("." + td):
            return True
    return False


def text_hits(patterns, text: str) -> bool:
    if not text:
        return False
    t = text.lower()
    for pat in patterns:
        if re.search(pat, t, flags=re.I):
            return True
    return False


def allow_item(title: str, summary: str, link: str) -> bool:
    """Notre Dame Football filter. Trusted domains bypass strict check."""
    # Trusted domain shortcut
    if is_trusted(link):
        # still avoid obviously wrong sports if title screams it
        if text_hits(RE_EXCLUDE, f"{title} {summary}"):
            return False
        return True

    blob = f"{title} {summary}".strip()
    if not blob:
        return False

    # Require ND + Football signals
    if not text_hits(RE_REQUIRED_ANY, blob):
        return False
    if not text_hits(RE_REQUIRED_SPORT, blob):
        return False
    if text_hits(RE_EXCLUDE, blob):
        return False

    # Basic non-noise title
    if len(title.strip()) < TITLE_LEN_MIN:
        return False

    return True


def normalize_item(raw, feed_name: str):
    link = raw.get("link") or ""
    title = strip_html(raw.get("title") or "").strip()
    summary = strip_html(raw.get("summary") or raw.get("description") or "").strip()
    published = choose_epoch(raw)

    # Avoid duplicate title in summary (common in feeds)
    s_low = summary.lower()
    t_low = title.lower()
    if summary and (s_low == t_low or s_low.startswith(t_low)):
        summary = summary[len(title):].strip(" -–:|") if len(summary) > len(title) else ""

    src = feed_name or hostname(link) or "Source"

    return {
        "title": title,
        "link": link,
        "summary": summary,
        "published": int(published),
        "source": src,
    }


def dedupe(items):
    seen = set()
    out = []
    for it in items:
        key = it["link"].strip().lower() or (it["title"].strip().lower(), it["source"].strip().lower())
        if key in seen:
            continue
        seen.add(key)
        out.append(it)
    return out


def collect_once(feeds):
    all_items = []
    for f in feeds:
        name = f.get("name") or ""
        url = f.get("url") or ""
        if not url:
            continue
        try:
            log(f"fetch: {name} — {url}")
            parsed = feedparser.parse(url)
            if parsed.bozo:
                log(f"  warn: feed bozo={parsed.bozo_exception!r}")
            # Some feeds put title at top-level
            feed_title = (parsed.feed.get("title") if parsed.feed else None) or name
            for entry in parsed.entries or []:
                item = normalize_item(entry, feed_title)
                if allow_item(item["title"], item["summary"], item["link"]):
                    all_items.append(item)
        except Exception as e:
            log(f"  error: {e}")
            traceback.print_exc()

    if not all_items:
        return []

    # sort newest first
    all_items.sort(key=lambda x: x["published"], reverse=True)
    # dedupe
    all_items = dedupe(all_items)
    # cap
    return all_items[:MAX_ITEMS]


def write_json(path: str, items):
    payload = {
        "team": APP_TITLE,
        "updated": int(time.time()),
        "count": len(items),
        "items": items,
    }
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)
    # atomic-ish replace
    import os
    os.replace(tmp, path)
    log(f"wrote {path} with {len(items)} items at {payload['updated']}")


def main():
    parser = argparse.ArgumentParser(description="Collect feeds into items.json")
    parser.add_argument("--out", default="items.json", help="Output JSON path (default: items.json)")
    args = parser.parse_args()

    feeds = load_feeds()
    if not feeds:
        log("No feed URLs available. Writing empty payload so the site stays up.")
        write_json(args.out, [])
        sys.exit(0)

    items = collect_once(feeds)
    write_json(args.out, items)
    log("done.")


if __name__ == "__main__":
    main()