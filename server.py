import json, os, time, traceback
from datetime import datetime, timezone
from flask import Flask, render_template, send_from_directory, jsonify, make_response

# ---- App ----
app = Flask(__name__, static_folder="static", template_folder="templates")

# Simple in-memory cache so we don't read the file on every request
STATE = {"items": [], "updated": 0, "feeds_meta": {}}
ITEMS_PATH = os.path.join(os.path.dirname(__file__), "items.json")
FEEDS_PATH = os.path.join(os.path.dirname(__file__), "feeds.json")

def _safe_load_json(path, default):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        print(f"[WARN] Failed reading {path}:")
        traceback.print_exc()
    return default

def _load_state():
    # items.json is optional — empty list is fine
    STATE["items"] = _safe_load_json(ITEMS_PATH, [])
    STATE["updated"] = int(time.time())
    STATE["feeds_meta"] = _safe_load_json(FEEDS_PATH, {"links": [], "feeds": []})

@app.after_request
def _no_cache(resp):
    # prevent stale CSS/JS while we're iterating
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    return resp

@app.route("/")
def index():
    if not STATE["updated"]:
        _load_state()
    # Render with a small initial snapshot; front-end fetches fresh list
    return render_template(
        "index.html",
        initial_items=STATE["items"][:40],
        last_updated_iso=datetime.now(timezone.utc).strftime("%-m/%-d/%Y, %-I:%M:%S %p"),
        version=str(int(time.time()))  # cache-bust static assets
    )

@app.route("/items.json")
def items_json():
    # Always reload from disk so a fresh collect write shows up immediately
    items = _safe_load_json(ITEMS_PATH, [])
    return jsonify({"items": items, "updated": int(time.time())})

@app.route("/feeds.json")
def feeds_json():
    meta = _safe_load_json(FEEDS_PATH, {"links": [], "feeds": []})
    return jsonify(meta)

# Health endpoint for Railway
@app.route("/health")
def health():
    return jsonify({"ok": True, "updated": STATE.get("updated", 0)})

# Static file fallback (useful in some hosts)
@app.route("/static/<path:path>")
def static_files(path):
    return send_from_directory(app.static_folder, path)

if __name__ == "__main__":
    # Local run
    _load_state()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))