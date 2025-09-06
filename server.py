import os, json, time, datetime as dt
from flask import Flask, render_template, request

app = Flask(__name__, static_url_path="/static")

ITEMS_PATH = os.environ.get("ITEMS_PATH", "items.json")

def _load_items():
    if not os.path.exists(ITEMS_PATH):
        return [], 0
    mtime = int(os.path.getmtime(ITEMS_PATH))
    try:
        with open(ITEMS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = []
    items = []
    for x in data:
        title = (x.get("title") or "").strip()
        summary = (x.get("summary") or "").strip()
        link = (x.get("link") or x.get("url") or "").strip()
        source = (x.get("source") or x.get("publisher") or "").strip()
        # normalize published
        ts = None
        for key in ("published_ts", "published", "date", "updated"):
            v = x.get(key)
            if isinstance(v, (int, float)):
                ts = int(v)
                break
            if isinstance(v, str) and v:
                # try parse RFC3339-ish
                try:
                    ts = int(dt.datetime.fromisoformat(v.replace("Z","")).timestamp())
                    break
                except Exception:
                    pass
        if ts is None:
            ts = mtime
        items.append({
            "title": title,
            "summary": summary,
            "link": link,
            "source": source,
            "published_ts": ts,
            "published_iso": dt.datetime.fromtimestamp(ts).isoformat(),
            "published_display": dt.datetime.fromtimestamp(ts).strftime("%-m/%-d/%Y, %-I:%M %p"),
        })
    # newest first
    items.sort(key=lambda i: i["published_ts"], reverse=True)
    return items, mtime

@app.route("/")
def home():
    items, items_mtime = _load_items()
    # build list of sources for the dropdown (sorted, unique)
    sources = sorted({i["source"] for i in items if i["source"]})
    sel = request.args.get("source", "").strip()
    if sel:
        items = [i for i in items if i["source"] == sel]

    updated_at = dt.datetime.fromtimestamp(items_mtime).strftime("%-m/%-d/%Y, %-I:%M:%S %p")
    # cache_buster changes whenever items.json changes (and at boot)
    cache_buster = f"{items_mtime}-{int(time.time())//3600}"
    return render_template(
        "index.html",
        items=items,
        sources=sources,
        selected_source=sel,
        updated_at=updated_at,
        cache_buster=cache_buster,
        team_name="Notre Dame Football",
    )

if __name__ == "__main__":
    # good defaults for local runs; Railway runs gunicorn from Procfile
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))