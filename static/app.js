/* static/app.js
   Minimal, layout-safe helpers:
   - Fight song toggle (no scroll/jump)
   - Sources dropdown navigation
   - Background check for new items.json -> show refresh button
*/

(() => {
  // ---- Config --------------------------------------------------------------
  const ITEMS_URL = "/items.json";     // served by Flask
  const POLL_MS   = 120000;            // check every 2 minutes (reasonable + safe)
  const SS_KEY    = "nd_items_hash";   // sessionStorage key for last seen content

  // ---- Helpers -------------------------------------------------------------
  function djb2Hash(str) {
    let h = 5381;
    for (let i = 0; i < str.length; i++) h = ((h << 5) + h) ^ str.charCodeAt(i);
    // Return short hex string
    return (h >>> 0).toString(16);
  }

  async function fetchItemsHash() {
    try {
      const res = await fetch(ITEMS_URL, { cache: "no-store" });
      if (!res.ok) return null;
      const data = await res.json();
      // Hash a stable, small subset to reduce noise
      const compact = JSON.stringify(
        Array.isArray(data?.items)
          ? data.items.map(i => [i.title, i.link, i.published]).slice(0, 200)
          : data
      );
      return djb2Hash(compact);
    } catch {
      return null;
    }
  }

  function softShow(el) {
    if (!el) return;
    el.style.display = "";
    el.hidden = false;
    el.ariaHidden = "false";
  }
  function softHide(el) {
    if (!el) return;
    el.style.display = "none";
    el.hidden = true;
    el.ariaHidden = "true";
  }

  // ---- Fight Song (no jump) -----------------------------------------------
  (function setupFightSong() {
    const btn   = document.getElementById("fightSongBtn");
    const audio = document.getElementById("fightSongAudio");
    if (!btn || !audio) return;

    // Ensure the button never causes anchor focus/scroll
    btn.addEventListener("click", async (e) => {
      e.preventDefault();
      e.stopPropagation();

      // iOS sometimes needs a user gesture to start audio; we're in one.
      try {
        if (audio.paused) {
          await audio.play();
          btn.dataset.state = "playing";
          // Optional: keep label stable if you prefer "Victory March" text
          // btn.textContent = "Pause";
          btn.setAttribute("aria-pressed", "true");
        } else {
          audio.pause();
          btn.dataset.state = "paused";
          // btn.textContent = "Victory March";
          btn.setAttribute("aria-pressed", "false");
        }
      } catch {
        // swallow—don’t pop errors to users
      }
    });

    // Keep UI consistent if song ends
    audio.addEventListener("ended", () => {
      btn.dataset.state = "paused";
      btn.setAttribute("aria-pressed", "false");
      // btn.textContent = "Victory March";
    });
  })();

  // ---- Sources dropdown (simple navigation) -------------------------------
  (function setupSourcesSelect() {
    const select = document.getElementById("sourceSelect");
    if (!select) return;
    select.addEventListener("change", () => {
      const v = select.value || "";
      const url = v ? `/?source=${encodeURIComponent(v)}` : "/";
      // Full navigation so server filters and SSR render do the work
      window.location.assign(url);
    });
  })();

  // ---- New items check -> "refresh" button --------------------------------
  (function setupUpdatePoll() {
    const row     = document.getElementById("newItemsRow");   // optional wrapper
    const refresh = document.getElementById("refreshBtn");     // the button itself

    if (refresh) {
      // Hidden by default in CSS; we control visibility explicitly
      softHide(row || refresh);
      refresh.addEventListener("click", (e) => {
        e.preventDefault();
        // Hard reload to pick up new items AND fresh CSS/JS if you just deployed
        window.location.reload();
      });
    }

    let pollTimer = null;

    async function primeBaseline() {
      const existing = sessionStorage.getItem(SS_KEY);
      if (existing) return; // already have a baseline this tab

      const h = await fetchItemsHash();
      if (h) sessionStorage.setItem(SS_KEY, h);
    }

    async function checkOnce() {
      // Don’t hammer while tab is backgrounded
      if (document.hidden) return;

      const prev = sessionStorage.getItem(SS_KEY) || "";
      const next = await fetchItemsHash();
      if (!next) return;

      if (!prev) {
        sessionStorage.setItem(SS_KEY, next);
        return;
      }

      if (next !== prev) {
        // New content available—invite the user to refresh
        softShow(row || refresh);
      }
    }

    function startPolling() {
      if (pollTimer) clearInterval(pollTimer);
      pollTimer = setInterval(checkOnce, POLL_MS);
    }

    // Initialize
    (async () => {
      await primeBaseline();
      startPolling();
    })();

    // Be polite with resources
    document.addEventListener("visibilitychange", () => {
      if (document.hidden) {
        if (pollTimer) clearInterval(pollTimer);
        pollTimer = null;
      } else {
        startPolling();
      }
    });
  })();
})();