#!/usr/bin/env python3
# collect.py — team-aware RSS collector for Sports App Project
# - Imports FEEDS from either root feeds.py or teams/<slug>/feeds.py
# - Filters for team/sport, dedups, caps at MAX_ITEMS
# - Writes JSON atomically (so the web app never reads a half-written file)

import os
import re
import sys
import time
import json
import html
import argparse
import tempfile
import importlib.util
from typing import List, Dict, Any, Tuple

import requests
import feedparser

# ---------- Tunables ----------
MAX_ITEMS = 50
REQUEST_TIMEOUT = (8, 15)  # (connect, read)
USER_AGENT = "sports-app-collector/1.0 (+https://example)"
SUMMARY_MAX_CHARS = 240

# Exclude terms (lowercased) that clearly aren't the target sport
EXCLUDE_TERMS = [
    "women", "wbb", "volleyball", "softball", "baseball", "soccer",
    "hockey", "lacrosse", "golf", "tennis", "track", "swim", "swimming",
    "cross country", "xc", "basketball", "womens", "women’s",
]

# Default include terms if team config doesn't provide KEYWORDS
DEFAULT_KEYWORDS = [
    # Team identity
    "notre dame", "fighting irish", "nd",
    # Sport identity
    "football", "ncaaf", "college football",
]

# ---------- Logging ----------
def log(msg: str) -> None:
    ts = time.strftime("%H:%M:%S")
    print(f"[collect {ts}] {msg}", flush=True)

# ---------- Utils ----------
def import_module_from_path(py_path: str):
    spec = importlib.util.spec_from_file_location("teamfeeds", py_path)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def load_feeds(team_slug: str | None) -> Tuple[List[Dict[str, Any]], List[Dict[str, str]], List[str]]:
    """
    Returns (FEEDS, STATIC_LINKS, KEYWORDS)
    - team_slug=None -> root feeds.py
    - else -> teams/<slug>/feeds.py if present, fallback to root feeds.py
    """
    # Try team-specific first
    if team_slug:
        team_path = os.path.join("teams", team_slug, "feeds.py")
        if os.path.exists(team_path):
            log(f"Using team feeds: {team_path}")
            mod = import_module_from_path(team_path)
            if mod:
                feeds = getattr(mod, "FEEDS", [])
                static_links = getattr(mod, "STATIC_LINKS", [])
                keywords = getattr(mod, "KEYWORDS", DEFAULT_KEYWORDS)
                return feeds, static_links, [k.lower() for k in keywords]

    # Fallback: root feeds.py
    root_path = os.path.join("feeds.py")
    if os.path.exists(root_path):
        log("Using root feeds.py")
        mod = import_module_from_path(root_path)
        if mod:
            feeds = getattr(mod, "FEEDS", [])
            static_links = getattr(mod, "STATIC_LINKS", [])
            keywords = getattr(mod, "KEYWORDS", DEFAULT_KEYWORDS)
            return feeds, static_links, [k.lower() for k in keywords]

    # If nothing found, return empty (collector still writes a valid JSON)
    log("WARNING: No feeds.py found; writing empty items.json")
    return [], [], [k.lower() for k in DEFAULT_KEYWORDS]

def http_get(url: str) -> bytes | None:
    try:
        resp = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=REQUEST_TIMEOUT,
        )
        if 200 <= resp.status_code < 300:
            return resp.content
        log(f"HTTP {resp.status_code} for {url}")
    except Exception as e:
        log(f"GET failed for {url}: {e}")
    return None

def parse_feed(content: bytes) -> feedparser.FeedParserDict:
    # feedparser accepts bytes directly
    return feedparser.parse(content)

def clean_text(s: str | None) -> str:
    if not s:
        return ""
    # strip HTML tags quickly; feedparser often gives plaintext but be safe
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def ts_from_entry(entry) -> int:
    for key in ("published_parsed", "updated_parsed", "created_parsed"):
        val = getattr(entry, key, None)
        if val:
            try:
                return int(time.mktime(val))
            except Exception:
                pass
    return int(time.time())

def summarize(s: str, max_chars: int = SUMMARY_MAX_CHARS) -> str:
    s = clean_text(s)
    if len(s) <= max_chars:
        return s
    # smart-ish truncation
    cut = s[: max_chars - 1]
    # try to end at word boundary
    cut = re.sub(r"\s+\S*$", "", cut).rstrip(",.;:-") + "…"
    return cut

def allow_item(title: str, summary: str, source_name: str, keywords: List[str], trusted: bool) -> bool:
    t = (title or "").lower()
    s = (summary or "").lower()

    # Trusted feeds pass unless they contain explicit excludes
    if trusted:
        for bad in EXCLUDE_TERMS:
            if bad in t or bad in s:
                return False
        return True

    # Exclusions first
    for bad in EXCLUDE_TERMS:
        if bad in t or bad in s:
            return False

    hay = f"{t} {s}"
    # Require at least one team identity AND football identity
    # If KEYWORDS provided, treat as a pool and require >=1 matches
    matched = any(k in hay for k in keywords)
    if not matched:
        return False

    return True

def normalize_source(feed_obj: Dict[str, Any]) -> Tuple[str, bool]:
    """Returns (source_name, trusted)"""
    name = str(feed_obj.get("name") or "").strip() or "Feed"
    trusted = bool(feed_obj.get("trusted"))
    return name, trusted

def build_item(entry, source_name: str) -> Dict[str, Any]:
    title = clean_text(getattr(entry, "title", "") or "")
    link = getattr(entry, "link", "") or ""
    # Prefer summary/detail, fallback to description/content if present
    summary = getattr(entry, "summary", "") or getattr(entry, "description", "") or ""
    # Some feeds put HTML/long content in 'content' list
    if not summary and getattr(entry, "content", None):
        try:
            summary = entry.content[0].value
        except Exception:
            pass
    summary = summarize(summary)

    published = ts_from_entry(entry)

    return {
        "title": title,
        "link": link,
        "summary": summary,
        "source": source_name,
        "published": published,
    }

def write_json_atomic(path: str, data: Dict[str, Any]) -> None:
    d = os.path.dirname(path) or "."
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".items.", suffix=".json", dir=d)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp, path)

# ---------- Main ----------
def main():
    ap = argparse.ArgumentParser(description="Collect and filter RSS items for Sports App.")
    ap.add_argument("--team", help="Team slug (uses teams/<slug>/feeds.py if present).", default=None)
    ap.add_argument("--out", help="Output JSON path (default: items.json)", default="items.json")
    args = ap.parse_args()

    feeds, _static_links, keywords = load_feeds(args.team)

    items: List[Dict[str, Any]] = []
    seen_links: set[str] = set()
    seen_titles: set[str] = set()

    total_entries = 0
    kept = 0

    for f in feeds:
        url = f.get("url")
        if not url:
            continue
        source_name, trusted = normalize_source(f)

        log(f"Fetching: {source_name} — {url}")
        content = http_get(url)
        if not content:
            continue

        parsed = parse_feed(content)
        entries = parsed.entries or []
        total_entries += len(entries)

        for entry in entries:
            try:
                item = build_item(entry, source_name)
            except Exception as e:
                log(f"Entry parse error: {e}")
                continue

            # Dedup by link (preferred), fallback to title
            key = item["link"] or item["title"]
            if not key:
                continue
            low_key = key.lower()
            if low_key in seen_links or item["title"].lower() in seen_titles:
                continue

            if allow_item(item["title"], item["summary"], source_name, keywords, trusted):
                items.append(item)
                seen_links.add(low_key)
                seen_titles.add(item["title"].lower())
                kept += 1

    # Sort newest first, cap at MAX_ITEMS
    items.sort(key=lambda x: x.get("published", 0), reverse=True)
    items = items[:MAX_ITEMS]

    payload = {
        "team": (args.team or "notre-dame-football"),
        "updated": int(time.time()),
        "count": len(items),
        "items": items,
    }

    try:
        write_json_atomic(args.out, payload)
        log(f"Wrote {len(items)} items to {args.out} (from {total_entries} entries across {len(feeds)} feeds)")
    except Exception as e:
        log(f"ERROR writing {args.out}: {e}")
        # Last resort: write non-atomic (should rarely happen)
        try:
            with open(args.out, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
            log(f"Fallback write succeeded: {args.out}")
        except Exception as e2:
            log(f"FATAL: Unable to write {args.out}: {e2}")
            sys.exit(2)

if __name__ == "__main__":
    main()
