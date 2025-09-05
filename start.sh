#!/usr/bin/env bash
set -euo pipefail

echo "[BOOT] PWD: $(pwd)"
echo "[BOOT] Python: $(python3 --version || python --version || true)"
echo "[BOOT] Listing repo root:"
ls -la

# Sanity: make sure server.py and 'app' exist before we even try to bind.
if [[ ! -f "server.py" ]]; then
  echo "[BOOT][FATAL] server.py not found at repo root. Did the repo get nested?"
  exit 9
fi

# Ensure PORT is set by Railway; default to 5000 for local runs.
export PORT="${PORT:-5000}"
echo "[BOOT] Binding on 0.0.0.0:${PORT}"

# Single, deterministic launcher: Gunicorn with light concurrency.
# (gthread keeps memory low; timeout generous for slow cold starts)
exec gunicorn \
  -w 2 \
  -k gthread \
  --threads 8 \
  --timeout 120 \
  --graceful-timeout 30 \
  --keep-alive 5 \
  --access-logfile - \
  --error-logfile - \
  -b 0.0.0.0:"${PORT}" \
  server:app
