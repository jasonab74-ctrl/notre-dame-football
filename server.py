# server.py — Flask app to serve the site + items.json + feeds.json
from flask import Flask, render_template, send_file, jsonify
import os, json, time

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route("/")
def index():
    return render_template("index.html")

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
    return send_file(path, mimetype="application/json")

@app.route("/feeds.json")
def feeds_json():
    # Expose FEEDS + STATIC_LINKS to the front end, like your Purdue app
    try:
        from feeds import FEEDS, STATIC_LINKS
    except Exception:
        FEEDS, STATIC_LINKS = [], []
    return jsonify({"feeds": FEEDS, "links": STATIC_LINKS})

if __name__ == "__main__":
    app.run(debug=True)
