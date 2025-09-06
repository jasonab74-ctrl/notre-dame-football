import json
import os
import time
from datetime import datetime, timezone
from flask import Flask, render_template, send_from_directory, make_response

app = Flask(__name__)

# A tiny “build id” so we can cache-bust CSS safely after each deploy
BUILD_ID = str(int(time.time()))

def load_items():
    """Return list of article dicts from items.json, never crash."""
    path = os.path.join(app.root_path, "items.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict) and "items" in data:
                return data["items"]
            if isinstance(data, list):
                return data
    except Exception:
        pass
    return []

@app.route("/")
def index():
    items = load_items()
    updated_utc = datetime.now(timezone.utc)
    # Render with a cache-busting build id so style changes show up immediately
    resp = make_response(
        render_template(
            "index.html",
            items=items,
            updated_iso=updated_utc.strftime("%-m/%-d/%Y, %-I:%M:%S %p"),
            build_id=BUILD_ID,
        )
    )
    # Prevent the HTML itself from being cached (helps during rapid fixes)
    resp.headers["Cache-Control"] = "no-store"
    return resp

@app.route("/healthz")
def healthz():
    return "ok", 200

# Optional: make sure CSS/JS aren’t aggressively cached during your fixes.
# (Browsers will still revalidate but the build_id query param is the main lever.)
@app.after_request
def add_no_cache_headers(resp):
    # Only apply to text/html; static files are requested with ?v=BUILD_ID anyway.
    if resp.mimetype == "text/html":
        resp.headers["Cache-Control"] = "no-store"
    return resp

# Serve any static assets (logo/audio) if you add them later
@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(os.path.join(app.root_path, "static"), filename)

if __name__ == "__main__":
    # For local testing only; Railway will use gunicorn
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))