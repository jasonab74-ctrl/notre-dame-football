# server.py — resilient Flask server (no gunicorn needed)
from flask import Flask, render_template, send_file, jsonify
import os, json, time

APP_TITLE = "Notre Dame Football"

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.get("/")
def index():
    try:
        return render_template("index.html", title=APP_TITLE)
    except Exception as e:
        # Keep the app up even if template missing
        return f"<h1>{APP_TITLE}</h1><p>Template error: {e}</p>", 200

@app.get("/items.json")
def items():
    path = "items.json"
    if not os.path.exists(path):
        return jsonify({
            "team": f"{APP_TITLE}",
            "updated": int(time.time()),
            "count": 0,
            "items": []
        })
    try:
        return send_file(path, mimetype="application/json")
    except Exception:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            try:
                data = json.load(f)
            except Exception:
                data = {"team": f"{APP_TITLE}", "updated": int(time.time()), "count": 0, "items": []}
        return jsonify(data)

@app.get("/feeds.json")
def feeds_json():
    try:
        from feeds import FEEDS, STATIC_LINKS
    except Exception:
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
    # Railway runs this via Procfile: python3 server.py
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
