import feedparser, time, json
from datetime import datetime

MAX_ITEMS = 50

from feeds import FEEDS

def allow_item(entry):
    return True

def normalize(entry, source):
    return {
        "title": entry.get("title", ""),
        "link": entry.get("link", ""),
        "summary": entry.get("summary", ""),
        "published": int(time.mktime(entry.get("published_parsed", time.gmtime()))),
        "source": source,
    }

def main():
    items = []
    for feed in FEEDS:
        try:
            parsed = feedparser.parse(feed["url"])
            for e in parsed.entries:
                if allow_item(e):
                    items.append(normalize(e, feed["name"]))
        except Exception as ex:
            print(f"Failed feed {feed['url']}: {ex}")
    items.sort(key=lambda x: x["published"], reverse=True)
    items = items[:MAX_ITEMS]
    data = {
        "team": "Notre Dame Football",
        "updated": int(time.time()),
        "count": len(items),
        "items": items,
    }
    with open("items.json", "w", encoding="utf-8") as f:
        json.dump(data, f)
    print(f"Wrote {len(items)} items")

if __name__ == "__main__":
    main()
