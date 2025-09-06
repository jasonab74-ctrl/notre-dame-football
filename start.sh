#!/usr/bin/env bash
set -euo pipefail

# Always run from repo root
cd "$(dirname "$0")"

echo "[BOOT] ---------- START ----------"
echo "[BOOT] PWD: $(pwd)"
echo "[BOOT] Python: $(python3 --version || true)"
echo "[BOOT] Listing repo root:"
ls -la

# 1) Sanity checks
if [[ ! -f "server.py" ]]; then
  echo "[BOOT][FATAL] server.py NOT found at repo root. Check Railway 'Root Directory' setting."
  exit 9
fi

# 2) Verify the Flask app object can be imported
echo "[BOOT] Import test: python3 -c 'import importlib; m=importlib.import_module(\"server\"); assert hasattr(m, \"app\")'"
python3 - <<'PY'
import importlib, sys
try:
    m = importlib.import_module("server")
    assert hasattr(m, "app"), "No 'app' in server.py"
    print("[BOOT] server:app import OK")
except Exception as e:
    print(f"[BOOT][FATAL] Import failed: {e}")
    sys.exit(8)
PY

# 3) Ensure gunicorn exists
if ! python3 -c "import gunicorn" 2>/dev/null; then
  echo "[BOOT][WARN] gunicorn not importable. Will try to install (one-time)."
  pip install --no-cache-dir gunicorn || true
fi

PORT="${PORT:-8000}"
echo "[BOOT] Binding on 0.0.0.0:${PORT}"

# 4) Start Gunicorn (preferred)
set +e
gunicorn \
  -w 2 \
  --threads 8 \
  -k gthread \
  --timeout 60 \
  --graceful-timeout 20 \
  --keep-alive 5 \
  --access-logfile - \
  --error-logfile - \
  -b 0.0.0.0:"${PORT}" \
  server:app
rc=$?
set -e

if [[ $rc -ne 0 ]]; then
  echo "[BOOT][WARN] Gunicorn exited with code $rc. Falling back to 'python3 server.py' to avoid 502."
  exec python3 server.py
fi