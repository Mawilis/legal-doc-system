#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

LOOPBACK="127.0.0.1"
EOS_URL="http://${LOOPBACK}:9095/kernel"
VITE_URL="http://${LOOPBACK}:5173/"
READY_TIMEOUT_SECONDS=30
EOS_PID=""
VITE_PID=""

if [[ -x "$ROOT_DIR/.venv/bin/python" ]]; then
  PYTHON="$ROOT_DIR/.venv/bin/python"
else
  PYTHON="$(command -v python3 || true)"
fi
if [[ -z "$PYTHON" ]]; then
  echo "[WILSY] Python runtime not found; install the project virtual environment first." >&2
  exit 1
fi
if ! command -v npm >/dev/null 2>&1; then
  echo "[WILSY] npm is required only to run the React/Vite frontend." >&2
  exit 1
fi

cleanup() {
  local pid
  for pid in "$VITE_PID" "$EOS_PID"; do
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
      kill -TERM "$pid" 2>/dev/null || true
    fi
  done
  for pid in "$VITE_PID" "$EOS_PID"; do
    if [[ -n "$pid" ]]; then wait "$pid" 2>/dev/null || true; fi
  done
}
trap cleanup EXIT INT TERM

is_ready() {
  curl --silent --show-error --fail --max-time 2 "$1" >/dev/null 2>&1
}

if is_ready "$EOS_URL"; then
  echo "[WILSY] Reusing the healthy Python EOS runtime at $EOS_URL"
else
  echo "[WILSY] Starting Python EOS from $ROOT_DIR"
  "$PYTHON" -m uvicorn tools.eos.api.server:app --host "$LOOPBACK" --port 9095 &
  EOS_PID=$!
  ready=0
  for ((second=0; second<READY_TIMEOUT_SECONDS*3; second++)); do
    if is_ready "$EOS_URL"; then ready=1; break; fi
    if ! kill -0 "$EOS_PID" 2>/dev/null; then
      echo "[WILSY] EOS exited before readiness. Inspect the Python startup output above." >&2
      exit 1
    fi
    sleep 0.333
  done
  if [[ "$ready" -ne 1 ]]; then
    echo "[WILSY] EOS did not become ready within ${READY_TIMEOUT_SECONDS}s." >&2
    exit 1
  fi
  echo "[WILSY] Python EOS is ready."
fi

if is_ready "$VITE_URL"; then
  echo "[WILSY] Reusing the existing Vite frontend at $VITE_URL"
  if [[ -n "$EOS_PID" ]]; then
    wait "$EOS_PID"
  else
    while true; do sleep 3600; done
  fi
else
  echo "[WILSY] Starting React/Vite presentation client."
  npm --prefix client run dev -- --host "$LOOPBACK" &
  VITE_PID=$!
  wait "$VITE_PID"
fi
