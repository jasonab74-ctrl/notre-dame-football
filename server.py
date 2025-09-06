from flask import Flask, render_template, send_from_directory, jsonify
import json, os, datetime

app = Flask(__name__, static_folder="static", template_folder="templates")

ITEMS_PATH = os.environ.get("ITEMS_PATH", os.path.join(os.path.dirname(__file__), "items.json"))

def load_items():
    try:
        with open(ITEMS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Ensure sane defaults
            for it in data:
                it["title"] = it.get("title", "").strip()
                it["link"] = it.get("link", "")
                it["summary"] = it.get("summary", "").strip()
                it["source"] = it.get("source", "").strip()
                it["published"] = it.get("published", "")
            return data
    except Exception:
        return []

@app.route("/")
def index():
    items = load_items()
    # build unique sources for dropdown
    sources = sorted(list({it.get("source","").strip() for it in items if it.get("source")}))
    updated = datetime.datetime.utcnow().strftime("%-m/%-d/%Y, %-I:%M:%S %p")
    return render_template("index.html", items=items, sources=sources, updated=updated)

@app.route("/health")
def health():
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")), debug=False)
