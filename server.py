import os
import json
from datetime import datetime, timezone
from flask import Flask, render_template, request, send_from_directory, abort, make_response

APP_TITLE = "Notre Dame Football"
ITEMS_PATH = os.path.join(os.path.dirname(__file__), "items.json")

app = Flask(__name__, static_folder="static", template_folder="templates")


def load_items():
    """Load articles from items.json safely."""
    if not os.path.exists(ITEMS_PATH):
        return []
    try:
        with open(ITEMS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Expect list of dicts; tolerate single dict wrapper like {"items":[...]}
        if isinstance(data, dict) and "items" in data and isinstance(data["items"], list):
            data = data["items"]
        if not isinstance(data, list):
            return []
        norm = []
        for it in data:
            if not isinstance(it, dict):
                continue
            title = (it.get("title") or "").strip()
            url = (it.get("url") or it.get("link") or "").strip()
            source = (it.get("source") or it.get("site") or "").strip()
            summary = (it.get("summary") or it.get("description") or "").strip()
            # published can be epoch int/str or ISO string
            published_raw = it.get("published") or it.get("published_at") or it.get("date")
            published = None
            if published_raw:
                try:
                    if isinstance(published_raw, (int, float)) or (isinstance(published_raw, str) and published_raw.isdigit()):
                        published = datetime.fromtimestamp(int(published_raw), tz=timezone.utc)
                    else:
                        published = datetime.fromisoformat(str(published_raw).replace("Z", "+00:00"))
                except Exception:
                    published = None
            norm.append({
                "title": title,
                "url": url,
                "source": source,
                "summary": summary,
                "published": published.isoformat() if published else None
            })
        return norm
    except Exception:
        # If items file is malformed, fail closed but keep site up
        return []


def css_version():
    """Use the style.css mtime as a cache-busting version token."""
    try:
        path = os.path.join(app.static_folder, "style.css")
        mtime = os.path.getmtime(path)
        return int(mtime)
    except Exception:
        return 1


@app.after_request
def no_cache(resp):
    """
    Disable caching for HTML/JSON responses so updates always show,
    but let static assets be cached (we bust with ?v= token).
    """
    ct = resp.headers.get("Content-Type", "")
    if "text/html" in ct or "application/json" in ct:
        resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        resp.headers["Pragma"] = "no-cache"
        resp.headers["Expires"] = "0"
    return resp


@app.route("/healthz")
def healthz():
    return "ok", 200


@app.route("/")
def index():
    items = load_items()

    # collect distinct sources
    sources = sorted({(it.get("source") or "").strip() for it in items if (it.get("source") or "").strip()})
    selected = request.args.get("source", "").strip()
    if selected:
        items = [it for it in items if (it.get("source") or "").strip() == selected]

    # human-friendly time for “Updated”
    updated_ts = None
    try:
        # latest published if available
        published_list = [
            datetime.fromisoformat(p) for p in [it.get("published") for it in items] if p
        ]
        if published_list:
            updated_ts = max(published_list)
    except Exception:
        updated_ts = None

    return render_template(
        "index.html",
        title=APP_TITLE,
        items=items,
        sources=sources,
        selected_source=selected,
        css_ver=css_version(),
        updated_at=updated_ts
    )


if __name__ == "__main__":
    # Dev run (Railway will use Procfile/gunicorn)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))