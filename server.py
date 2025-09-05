# server.py — resilient boot version
from flask import Flask, render_template, send_file, jsonify
import os, json, time

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route("/")
def index():
    # Serve index even if templates/index.html missing
    try:
        return render_template("index.html")
    except Exception as e:
        return f"<h1>Notre Dame Football</h1><p>Template error: {e}</p>", 200

@app.route("/items.json")
def items():
    path = "items.json"
    if not os.path.exists(path):
        bootstrap = {
            "team": "Notre Dame Fighting Irish — Football",
            "updated": int(time.time()),
            "count": 0,
            "items": []
        }
        return jsonify(bootstrap)
    try:
        return send_file(path, mimetype="application/json")
    except Exception:
        # If file locked/corrupt, return safe payload
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            try:
                data = json.load(f)
            except Exception:
                data = {"team":"Notre Dame Fighting Irish — Football","updated":int(time.time()),"count":0,"items":[]}
        return jsonify(data)

@app.route("/feeds.json")
def feeds_json():
    try:
        from feeds import FEEDS, STATIC_LINKS
    except Exception:
        FEEDS, STATIC_LINKS = [], []
    return jsonify({"feeds": FEEDS, "links": STATIC_LINKS})

@app.route("/health")
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
            status["note"] = "items.json not found yet (will appear after collect.py runs)"
    except Exception as e:
        status["ok"] = False
        status["error"] = str(e)
    return jsonify(status)

if __name__ == "__main__":
    # Local/dev runner (Railway can also run this if you set Start Command to python3 server.py)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)
