# collect.py — fetch feeds and write items.json for GitHub Pages
import json, time, hashlib
from datetime import datetime, timezone
import feedparser, requests
from urllib.parse import urlparse
from feeds import FEEDS

MAX_ITEMS = 50

def norm_source(name, link):
    if name: return name.strip()
    try:
        host = urlparse(link or "").hostname or ""
        return host.replace("www.", "") or "Unknown"
    except:
        return "Unknown"

def clean_text(s):
    if not s: return ""
    return " ".join(str(s).split())

def allow_item(title, summary, source):
    t = f"{title} {summary}".lower()
    # positive signals
    if ("notre dame" in t or "fighting irish" in t or "south bend" in t or "nd" in t) and "football" in t:
        pass
    elif any(k in (source or "").lower() for k in ["onefootdown","usatoday","on3","rivals","southbendtribune","247sports","cbssports","espn.com","reddit.com"]):
        pass
    else:
        return False
    # exclusions
    exclude = ["women", "wbb", "volleyball", "softball", "basketball", "soccer"]
    if any(x in t for x in exclude):
        return False
    return True

def dedupe(items):
    seen = set()
    out = []
    for it in items:
        key = hashlib.md5((it.get("title","") + it.get("link","")).encode("utf-8")).hexdigest()
        if key in seen: 
            continue
        seen.add(key)
        out.append(it)
    return out

def fetch_all():
    items = []
    for f in FEEDS:
        url = f["url"]
        try:
            if "reddit.com" in url:
                r = requests.get(url, headers={"User-Agent":"nd-bot/1.0"}, timeout=20)
                parsed = feedparser.parse(r.text)
            else:
                parsed = feedparser.parse(url)
            feed_title = getattr(parsed.feed, "title", "") or f.get("name","")
            for e in parsed.entries[:80]:
                title = clean_text(getattr(e, "title", ""))
                summary = clean_text(getattr(e, "summary", ""))
                link = getattr(e, "link", "")
                published = getattr(e, "published", "") or getattr(e, "updated", "")
                source = norm_source(feed_title, link)
                if allow_item(title, summary, source):
                    items.append({
                        "title": title,
                        "summary": summary[:400],
                        "link": link,
                        "source": source,
                        "published": published
                    })
        except Exception:
            continue
        time.sleep(0.4)
    items = dedupe(items)
    items.sort(key=lambda x: x.get("published",""), reverse=True)
    return items[:MAX_ITEMS]

def main():
    items = fetch_all()
    data = {
        "updated": datetime.now(timezone.utc).isoformat(),
        "items": items
    }
    with open("items.json","w",encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(items)} items to items.json")

if __name__ == "__main__":
    main()
