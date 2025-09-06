#!/usr/bin/env bash
set -euo pipefail

# Always run from the app root
cd "$(dirname "$0")"

echo "[BOOT] Using Python: $(python3 --version)"
echo "[BOOT] Binding on 0.0.0.0:${PORT:-8000}"

# Gunicorn tuned for small Railway dynos and Flask
# - gthread avoids the old gevent headaches
# - 2 workers, 8 threads keeps memory modest
# - longer timeout keeps health checks happy during short GC pauses
exec gunicorn \
  -w 2 \
  --threads 8 \
  -k gthread \
  --timeout 60 \
  --graceful-timeout 20 \
  --keep-alive 5 \
  -b 0.0.0.0:"${PORT:-8000}" \
  server:app