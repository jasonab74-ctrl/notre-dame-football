import json
import os
from datetime import datetime
from flask import Flask, render_template, send_from_directory, request

app = Flask(__name__, static_folder="static", template_folder="templates")

# --- Helpers ---------------------------------------------------------------

def clean_summary(text: str) -> str:
    if not text:
        return ""
    # Replace common HTML non-breaking spaces and collapse excess whitespace
    cleaned = (
        text.replace("&nbsp;", " ")
            .replace("\u00a0", " ")
            .replace("&amp;", "&")
    )
    return " ".join(cleaned.split())

def fmt_ts(ts: str) -> str:
    """
    Accepts an ISO-like timestamp string (e.g., '2025-09-06T12:00:10+00:00')
    and renders 'Sep 6, 2025, 12:00 PM' in the server's local time.
    Falls back gracefully if parsing fails.
    """
    if not ts:
        return ""
    try:
        # Try multiple common formats
        for fmt in ("%Y-%m-%dT%H:%M:%S%z",
                    "%Y-%m-%dT%H:%M:%S.%f%z",
                    "%Y-%m-%d %H:%M:%S%z",
                    "%Y-%m-%dT%H:%M:%S",
                    "%Y-%m-%d %H:%M:%S"):
            try:
                dt = datetime.strptime(ts, fmt)
                break
            except ValueError:
                dt = None
        if dt is None:
            # Last-ditch: strip timezone colon if present and try again
            if ts.endswith(":00"):
                ts2 = ts[:-3] + ts[-3:]  # naive tweak; keep original if fails
            else:
                ts2 = ts
            dt = datetime.fromisoformat(ts2.replace("Z", "+00:00"))
        return dt.strftime("%b %-d, %Y, %-I:%M %p") if os.name != "nt" else dt.strftime("%b %d, %Y, %I:%M %p").lstrip("0").replace(" 0", " ")
    except Exception:
        # Show raw if we truly cannot parse
        return ts

def load_items():
    path = os.path.join(os.path.dirname(__file__), "items.json")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Normalize items
    items = []
    for it in data:
        items.append({
            "title": it.get("title", "").strip(),
            "link": it.get("link") or it.get("url") or "#",
            "summary": clean_summary(it.get("summary", it.get("description", ""))),
            "source": it.get("source", it.get("site", "Google News")),
            "published_raw": it.get("published") or it.get("date") or "",
            "published": fmt_ts(it.get("published") or it.get("date") or "")
        })
    return items

def build_nav():
    # Keep exactly your current set; adjust labels/urls only if you want later
    return [
        ("Official Site", "https://fightingirish.com/sports/football/"),
        ("Schedule", "https://www.espn.com/college-football/team/schedule/_/id/87/notre-dame-fighting-irish"),
        ("Roster", "https://www.espn.com/college-football/team/roster/_/id/87/notre-dame-fighting-irish"),
        ("CFB Rankings", "https://www.espn.com/college-football/rankings"),
        ("ND Insider", "https://www.ndinsider.com/"),
        ("Reddit — r/notredamefootball", "https://www.reddit.com/r/notredamefootball/"),
        ("YouTube — ND Football", "https://www.youtube.com/channel/UCAMR05qSc5mfhVx20fDyAoQ"),
        ("247Sports ND", "https://247sports.com/college/notre-dame/"),
        ("ESPN ND Football", "https://www.espn.com/college-football/team/_/id/87/notre-dame-fighting-irish"),
        ("CBS Sports ND", "https://www.cbssports.com/college-football/teams/ND/notre-dame-fighting-irish/"),
        ("On3 — Blue & Gold", "https://www.on3.com/teams/notre-dame-fighting-irish/"),
        ("The Athletic — ND", "https://theathletic.com/college-football/team/notre-dame-fighting-irish/"),
        ("Fighting Irish Wire", "https://fightingirishwire.usatoday.com/")
    ]

def build_sources(items):
    # Unique source names for the dropdown
    names = sorted({it["source"] for it in items if it.get("source")})
    return ["All sources"] + names

# --- Routes ----------------------------------------------------------------

@app.route("/")
def index():
    items = load_items()

    # filter by ?source=Name (optional)
    source = request.args.get("source")
    if source and source != "All sources":
        items = [it for it in items if it.get("source") == source]

    # pick a display timestamp: newest item or now if empty
    if items and items[0].get("published"):
        updated_display = items[0]["published"]
    else:
        updated_display = datetime.utcnow().strftime("%b %d, %Y, %I:%M %p").lstrip("0").replace(" 0", " ")

    return render_template(
        "index.html",
        title="Notre Dame Football",
        updated=updated_display,
        nav_links=build_nav(),
        sources=build_sources(load_items()),
        current_source=source or "All sources",
        items=items
    )

# Static (cache headers kept short so CSS/JS changes show up)
@app.after_request
def add_cache_headers(resp):
    if request.path.startswith("/static/"):
        resp.headers["Cache-Control"] = "public, max-age=120"
    return resp

@app.route("/favicon.ico")
def favicon():
    return send_from_directory(app.static_folder, "favicon.ico")

# Railway/Heroku style entrypoint
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)