import os, json, time, traceback
from flask import Flask, jsonify, Response, send_file

APP_TITLE = "Notre Dame Football"

def log(msg: str):
    print(f"[SERVER] {msg}", flush=True)

app = Flask(__name__, static_folder="static", template_folder="templates")

@app.get("/")
def index():
    return app.send_static_file("index.html")

@app.get("/items.json")
def items():
    path = "items.json"
    if not os.path.exists(path):
        log("items.json not found — returning empty payload")
        return jsonify({"team": APP_TITLE, "updated": int(time.time()), "count": 0, "items": []})
    try:
        return send_file(path, mimetype="application/json")
    except Exception:
        log("send_file failed, falling back to json.load")
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                data = json.load(f)
        except Exception as e:
            log(f"items.json invalid: {e}")
            data = {"team": APP_TITLE, "updated": int(time.time()), "count": 0, "items": []}
        return jsonify(data)

@app.get("/feeds.json")
def feeds_json():
    try:
        from feeds import FEEDS, STATIC_LINKS
    except Exception as e:
        log(f"feeds import failed: {e}")
        FEEDS, STATIC_LINKS = [], []
    return jsonify({"feeds": FEEDS, "links": STATIC_LINKS})

@app.get("/health")
def health():
    status = {"ok": True, "updated": None, "count": 0, "now": int(time.time())}
    try:
        if os.path.exists("items.json"):
            with open("items.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                status["updated"] = int(data.get("updated") or 0)
                status["count"] = int(data.get("count") or 0)
        else:
            status["ok"] = False
            status["note"] = "items.json not found yet (run collect.py or cron)"
    except Exception as e:
        status["ok"] = False
        status["error"] = str(e)
    return jsonify(status)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    log(f"Starting Flask on 0.0.0.0:{port}")
    try:
        app.run(host="0.0.0.0", port=port, debug=False)
    except Exception as e:
        log(f"CRASH on startup: {e}")
        traceback.print_exc()
        raise
