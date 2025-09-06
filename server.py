# server.py — stable Flask server (no network calls)
import os, json, time, traceback
from flask import Flask, jsonify, Response, send_file, request

APP_TITLE = "Notre Dame Football"

def log(msg: str):
    print(f"[SERVER] {msg}", flush=True)

app = Flask(__name__, static_folder="static")

HTML = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{APP_TITLE} — News</title>
  <link rel="icon" href="/static/favicon.ico" sizes="any">
  <link rel="apple-touch-icon" href="/static/apple-touch-icon.png">
  <link rel="manifest" href="/static/manifest.webmanifest">
  <meta name="theme-color" content="#0C2340">
  <link rel="stylesheet" href="/static/style.css" />
  <style>
    /* minimal safety if style.css misses something */
    body{{background:#0c2340;color:#e6edf3;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;margin:0}}
    .wrapper{{max-width:1100px;margin:0 auto;padding:18px}}
    .header{{display:flex;gap:16px;align-items:center;flex-wrap:wrap}}
    .logo{{width:64px;height:64px}}
    h1{{margin:0;line-height:1.1}}
    .muted{{opacity:.75;font-size:.9rem}}
    .links{{
      display:flex;flex-wrap:wrap;gap:12px;margin:14px 0 8px;
      border-bottom:1px solid rgba(255,255,255,.15);padding-bottom:12px
    }}
    .pill{{background:#c1992d;color:#0c2340;border:none;border-radius:999px;padding:10px 16px;font-weight:700;cursor:pointer;text-decoration:none;display:inline-block}}
    .select{{background:#0f2a55;border:1px solid rgba(255,255,255,.15);color:#e6edf3;border-radius:10px;padding:10px 12px}}
    .controls{{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin:10px 0}}
    .notice{{background:#143463;border:1px solid rgba(255,255,255,.15);padding:8px 12px;border-radius:10px}}
    .hidden{{display:none}}
    .grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}}
    @media (max-width:980px){{.grid{{grid-template-columns:repeat(2,1fr)}}}}
    @media (max-width:680px){{.grid{{grid-template-columns:1fr}}}}
    .card{{
      background:#f5e9c8;color:#1b1f23;border-radius:16px;padding:18px;box-shadow:0 1px 0 rgba(0,0,0,.05)
    }}
    .card a{{color:inherit;text-decoration:none}}
    .card h3{{margin:0 0 8px;font-size:1.15rem;line-height:1.25}}
    .summary{{margin:0 0 10px;opacity:.9}}
    .meta{{display:flex;gap:8px;align-items:center;opacity:.7;font-size:.9rem}}
    .dot::before{{content:"•"}}
    header .right{{margin-left:auto}}
  </style>
</head>
<body>
  <div class="wrapper">
    <header class="header">
      <img class="logo" src="/static/notre-dame-logo.png" alt="Notre Dame logo" />
      <div>
        <h1>Notre Dame<br/>Football</h1>
        <div id="updated" class="muted">Updated: —</div>
      </div>
      <div class="right">
        <button id="play-fight-song" class="pill">Victory March</button>
        <audio id="fight-song" src="/static/fight-song.mp3" preload="auto"></audio>
      </div>
    </header>

    <nav id="links" class="links"></nav>

    <section class="controls">
      <label for="sourceSel" class="muted">Sources:</label>
      <select id="sourceSel" class="select"><option value="__all__">All sources</option></select>
      <div id="notice" class="notice hidden">New items available — <button id="reload" class="pill">refresh</button></div>
    </section>

    <main id="feed" class="grid"></main>
  </div>

  <script>
    const fmtTime = (ts) => ts ? new Date(ts * 1000).toLocaleString() : "";
    const elUpdated = document.getElementById('updated');
    const elFeed = document.getElementById('feed');
    const elNotice = document.getElementById('notice');
    const elReload = document.getElementById('reload');
    const elLinks = document.getElementById('links');
    const elSource = document.getElementById('sourceSel');
    const fightBtn = document.getElementById('play-fight-song');
    const audio = document.getElementById('fight-song');

    // fight song toggle without layout jump
    fightBtn?.addEventListener('click', () => {
      if (audio.paused) { audio.currentTime = 0; audio.play(); fightBtn.textContent = '⏸ Victory March'; }
      else { audio.pause(); fightBtn.textContent = 'Victory March'; }
    });

    let lastCount = 0;
    let currentSource = "__all__";
    let cache = { items: [], updated: 0 };

    // build the top buttons + source dropdown from /feeds.json
    async function hydrateMeta() {
      try {
        const meta = await (await fetch('/feeds.json', {cache:'no-store'})).json();
        const links = meta.links || [];
        elLinks.innerHTML = links.map(l => `<a class="pill" href="${l.href}" target="_blank" rel="noopener">${l.label}</a>`).join('');
        const feeds = meta.feeds || [];
        const opts = feeds.map(f => `<option value="${(f.name||'').toLowerCase()}">${f.name}</option>`).join('');
        elSource.insertAdjacentHTML('beforeend', opts);
      } catch (e) { console.warn('feeds.json unavailable', e); }
    }

    function safeSummary(item) {
      const t = (item.title || "").trim();
      const s = (item.summary || "").trim();
      if (!s) return "";
      // avoid duplicate title-in-summary echoes
      if (s.toLowerCase() === t.toLowerCase()) return "";
      if (s.toLowerCase().startsWith(t.toLowerCase())) return s.slice(t.length).trim();
      return s;
    }

    function render(items) {
      const filtered = currentSource === "__all__"
        ? items
        : items.filter(i => (i.source || '').toLowerCase() === currentSource);

      elFeed.innerHTML = (filtered || []).map(item => {
        const summary = safeSummary(item);
        return `
        <article class="card">
          <a href="${item.link}" target="_blank" rel="noopener">
            <h3>${item.title || ''}</h3>
            ${summary ? `<p class="summary">${summary}</p>` : ''}
            <div class="meta">
              <span class="source">${item.source || ''}</span>
              <span class="dot"></span>
              <span class="time">${fmtTime(item.published)}</span>
            </div>
          </a>
        </article>`;
      }).join('');
    }

    async function load(initial=false) {
      const res = await fetch('/items.json', { cache: 'no-store' });
      const data = await res.json();
      cache = data;
      elUpdated.textContent = 'Updated: ' + fmtTime(data.updated);
      if (!initial && data.count > lastCount) elNotice.classList.remove('hidden');
      lastCount = data.count;
      render(data.items || []);
    }

    elReload?.addEventListener('click', () => {
      elNotice.classList.add('hidden');
      load(true);
    });

    elSource.addEventListener('change', (e) => {
      currentSource = (e.target.value || "__all__").toLowerCase();
      render(cache.items || []);
    });

    hydrateMeta();
    load(true);

    // Passive check every 5 minutes (no heavy work, only /items.json)
    setInterval(async () => {
      try {
        const data = await (await fetch('/items.json', { cache: 'no-store' })).json();
        if (data.count > lastCount) elNotice.classList.remove('hidden');
      } catch (_) {}
    }, 5 * 60 * 1000);
  </script>
</body>
</html>
"""

@app.after_request
def add_cors(resp):
    if resp.mimetype in ("application/json", "text/json") or request.path.startswith("/static/teams/"):
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Cache-Control"] = "max-age=60"
    return resp

@app.get("/")
def index():
    return Response(HTML, mimetype="text/html")

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