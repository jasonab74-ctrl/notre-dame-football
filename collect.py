import feedparser, re, json, time, datetime, hashlib, html
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from feeds.py import FEEDS  # noqa

OUT = "items.json"
MAX_ITEMS = 120

def clean_html(text):
    if not text:
        return ""
    soup = BeautifulSoup(text, "html.parser")
    txt = soup.get_text(" ", strip=True)
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt

def source_from_link(link, default=""):
    try:
        host = urlparse(link).netloc.lower()
        host = host.replace("www.", "")
        return host or default
    except Exception:
        return default

def normalize_item(entry, feed_title=""):
    title = html.unescape(entry.get("title", "")).strip()
    link = entry.get("link", "").strip()
    summary = clean_html(entry.get("summary", "") or entry.get("description", ""))
    published_parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if published_parsed:
        ts = time.strftime("%Y-%m-%dT%H:%M:%S%z", published_parsed)
    else:
        ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    src = feed_title or source_from_link(link)
    return {
        "id": hashlib.md5((title + link).encode("utf-8")).hexdigest(),
        "title": title,
        "link": link,
        "summary": summary,
        "source": src,
        "published": ts,
    }

def main():
    items = []
    for url in FEEDS:
        feed = feedparser.parse(url)
        ftitle = feed.get("feed", {}).get("title", "")
        for e in feed.get("entries", []):
            items.append(normalize_item(e, ftitle))
    # de-dup by id preserving order
    seen = set(); uniq = []
    for it in items:
        if it["id"] in seen: continue
        seen.add(it["id"]); uniq.append(it)
    # trim and sort by published desc (best-effort if ISO)
    uniq = uniq[:MAX_ITEMS]
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(uniq, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(uniq)} items to {OUT}")

if __name__ == "__main__":
    main()
