from __future__ import annotations
import os, json, time
from datetime import datetime, timezone
from flask import Flask, render_template, jsonify, make_response, send_from_directory

APP_NAME = "Notre Dame Football — News & Feeds"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "items.json")   # expected to exist already

app = Flask(__name__, static_folder="static", template_folder="templates")

# Disable static caching so new CSS/JS takes effect immediately in Railway
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

# A build/version token used for cache-busting query strings
BUILD_ID = os.environ.get("BUILD_ID") or str(int(time.time()))

def _read_items() -> list[dict]:
    """Read items.json; normalize minimal fields so template never breaks."""
    if not os.path.exists(DATA_PATH):
        return []
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except Exception:
        return []

    items = []
    for it in raw:
        title = it.get("title") or it.get("headline") or "Untitled"
        link = it.get("link") or it.get("url") or "#"
        source = (it.get("source") or it.get("site") or "").strip()
        summary = (it.get("summary") or it.get("description") or "").strip()
        # published can be iso, epoch, or missing
        pub = it.get("published") or it.get("date") or it.get("time") or ""
        published_ts = None
        if isinstance(pub, (int, float)):
            try:
                published_ts = datetime.fromtimestamp(float(pub), tz=timezone.utc)
            except Exception:
                published_ts = None
        elif isinstance(pub, str):
            for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S.%f%z",
                        "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
                try:
                    published_ts = datetime.strptime(pub, fmt)
                    if published_ts.tzinfo is None:
                        published_ts = published_ts.replace(tzinfo=timezone.utc)
                    break
                except Exception:
                    continue

        items.append({
            "title": title.strip(),
            "link": link,
            "source": source or "Google News",
            "summary": summary,
            "published_iso": published_ts.astimezone(timezone.utc).isoformat(timespec="seconds") if published_ts else "",
            "published_display": published_ts.astimezone(timezone.utc).strftime("%-m/%-d/%Y, %-I:%M %p") if published_ts else "",
        })
    return items

@app.after_request
def _no_store(resp):
    """Stop intermediaries from caching HTML/JSON. Static files already set to 0 max age."""
    if resp.content_type and ("text/html" in resp.content_type or "application/json" in resp.content_type):
        resp.headers["Cache-Control"] = "no-store, max-age=0"
        resp.headers["Pragma"] = "no-cache"
    return resp

@app.route("/")
def index():
    items = _read_items()
    updated_at = datetime.now(timezone.utc).strftime("%-m/%-d/%Y, %-I:%M:%S %p")
    return render_template(
        "index.html",
        app_name=APP_NAME,
        updated_at=updated_at,
        items=items,
        build_id=BUILD_ID,
    )

@app.route("/api/articles")
def api_articles():
    return jsonify({"items": _read_items(), "build_id": BUILD_ID})

@app.route("/health")
def health():
    return "ok"

# Optional: serve /favicon.ico if you dropped one in /static
@app.route("/favicon.ico")
def favicon():
    return send_from_directory(app.static_folder, "favicon.ico")

if __name__ == "__main__":
    # For local dev only; on Railway use gunicorn as you already do
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))