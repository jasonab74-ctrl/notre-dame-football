# server.py — single-file Flask app
import os, json, time, traceback
from flask import Flask, jsonify, Response, send_file

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
  <link rel="icon" type="image/png" sizes="32x32" href="/static/favicon-32x32.png">
  <link rel="apple-touch-icon" href="/static/apple-touch-icon.png">
  <link rel="manifest" href="/static/manifest.webmanifest">
  <meta name="theme-color" content="#0C2340">
  <link rel="stylesheet" href="/static/style.css" />
</head>
<body>
  <header class="header">
    <img class="logo" src="/static/notre-dame-logo.png" alt="Notre Dame logo" />
    <div>
      <h1>Notre Dame<br/>Football</h1>
      <div id="updated" class="muted">Updated: —</div>
    </div>
    <button id="play-fight-song" class="pill">Victory March</button>
    <audio id="fight-song" src="/static/fight-song.mp3" preload="auto"></audio>
  </header>

  <nav id="links" class="links"></nav>

  <section class="controls">
    <label for="sourceSel" class="muted">Sources:</label>
    <select id="sourceSel" class="select">
      <option value="__all__">All sources</option>
    </select>
    <div id="notice" class="notice hidden">New items available — <button id="reload" class="pill">refresh</button></div>
  </section>

  <main id="feed" class="grid"></main>

  <footer class="footer">
    <span>Built with your Sports App template.</span>
  </footer>

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

    fightBtn?.addEventListener('click', () => {
      if (audio.paused) { audio.currentTime = 0; audio.play(); fightBtn.textContent = '⏸ Victory March'; }
      else { audio.pause(); fightBtn.textContent = 'Victory March'; }
    });

    let lastCount = 0;
    let currentSource = "__all__";
    let cache = { items: [], updated: 0 };

    async function hydrateMeta() {
      try {
        const meta = await (await fetch('/feeds.json', {cache:'no-store'})).json();
        const links = meta.links || [];
        elLinks.innerHTML = links.map(l => `<a class="pill" href="${l.href}" target="_blank" rel="noopener">${l.label}</a>`).join('');
        const feeds = meta.feeds || [];
        const opts = feeds.map(f => `<option value="${f.name}">${f.name}</option>`).join('');
        elSource.insertAdjacentHTML('beforeend', opts);
      } catch (e) {
        console.warn('feeds.json unavailable', e);
      }
    }

    function cleanSummary(title, summary) {
      let s = (summary || "").trim();
      if (!s) return "";
      // If identical to title or begins with title, drop it
      const t = (title || "").trim();
      if (t && (s === t || s.toLowerCase().startsWith(t.toLowerCase()))) s = "";
      // Strip repeated whitespace and trailing source fragments
      s = s.replace(/\\s+/g,' ').replace(/\\s*[|—-]\\s*[^|—-]+$/,'').trim();
      // Clamp length
      const MAX = 220;
      if (s.length > MAX) s = s.slice(0, MAX-1).trim() + "…";
      return s;
    }

    function render(items) {
      const filtered = currentSource === "__all__"
        ? items
        : items.filter(i => (i.source || '').toLowerCase() === currentSource.toLowerCase());

      elFeed.innerHTML = (filtered || []).map(item => {
        const title = item.title || '';
        const summary = cleanSummary(title, item.summary);
        const summaryHtml = summary ? `<p class="summary">${summary}</p>` : '';
        return `
        <article class="card">
          <a href="${item.link}" target="_blank" rel="noopener">
            <h3>${title}</h3>
            ${summaryHtml}
            <div class="meta">
              <span class="source">${item.source || ''}</span>
              <span class="dot">•</span>
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
      currentSource = e.target.value || "__all__";
      render(cache.items || []);
    });

    hydrateMeta();
    load(true);
    setInterval(async () => {
      try {
        const res = await fetch('/items.json', { cache: 'no-store' });
        const data = await res.json();
        if (data.count > lastCount) elNotice.classList.remove('hidden');
      } catch {}
    }, 5 * 60 * 1000);
  </script>
</body>
</html>
"""

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