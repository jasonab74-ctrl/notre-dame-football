import os, json, datetime
from flask import Flask, render_template, request

app = Flask(__name__, static_folder="static", template_folder="templates")

# -------- helpers --------
def _load_items():
    try:
        with open("items.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            items = data if isinstance(data, list) else data.get("items", [])
    except Exception:
        items = []

    # normalize fields so template never breaks
    normalized = []
    for it in items:
        normalized.append({
            "title": it.get("title") or it.get("headline") or "(untitled)",
            "summary": it.get("summary") or it.get("description") or "",
            "link": it.get("link") or it.get("url") or "#",
            "source": it.get("source") or it.get("site") or it.get("source_name") or "Unknown",
            "published": it.get("published") or it.get("date") or "",
        })
    return normalized

def _updated_and_buster():
    if os.path.exists("items.json"):
        ts = os.path.getmtime("items.json")
    else:
        ts = datetime.datetime.utcnow().timestamp()
    # nice readable time (no leading zeroes) and an integer cache-buster
    updated_dt = datetime.datetime.fromtimestamp(ts)
    updated_str = updated_dt.strftime("%m/%d/%Y, %I:%M:%S %p").replace("/0", "/").lstrip("0")
    return updated_str, int(ts)

# -------- no-cache for HTML responses --------
@app.after_request
def add_no_cache_headers(resp):
    # Prevent HTML from being cached; static files get cache-busted via ?v= param.
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp

# -------- routes --------
@app.route("/")
def index():
    selected = request.args.get("source", "all")
    items = _load_items()

    # unique sources from items (server-rendered so no JS required)
    sources = sorted({it["source"] for it in items if it.get("source")})

    if selected != "all":
        items = [it for it in items if it["source"] == selected]

    updated, cache_buster = _updated_and_buster()
    return render_template(
        "index.html",
        items=items,
        sources=sources,
        selected_source=selected,
        updated=updated,
        cache_buster=cache_buster,
    )

if __name__ == "__main__":
    # For local run; Railway will use your Procfile/gunicorn
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))