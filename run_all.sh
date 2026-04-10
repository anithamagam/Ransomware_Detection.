#!/usr/bin/env bash
set -euo pipefail

# Start the project's Python main process and the frontend dev server.
# The frontend and main run side-by-side; there is no HTTP bridge since the
# FastAPI backend was removed per request.

ROOT_DIR=$(dirname "$0")
cd "$ROOT_DIR"

echo "Ensure you have a virtualenv active and dependencies installed:"
echo "  python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"

# Start Python main in background (training may take long)
echo "Starting main.py in background (logs -> main.log)"
python main.py --dataset Datasets/Drebin_v1.csv --algorithm KNN > main.log 2>&1 &
MAIN_PID=$!

function finish {
  echo "Stopping main (pid $MAIN_PID)"
  kill "$MAIN_PID" 2>/dev/null || true
}
trap finish EXIT

# Start frontend dev server if frontend exists
if [ -d "frontend" ]; then
  echo "Starting frontend dev server"
  cd frontend
  if [ -f package.json ]; then
    if command -v pnpm >/dev/null 2>&1; then
      pnpm install
      # bind to all interfaces so the devcontainer forwards the port
      pnpm run dev -- --host 0.0.0.0 --port 5173
    else
      npm install
      npm run dev -- --host 0.0.0.0 --port 5173
    fi
  else
    echo "No package.json in frontend; nothing to run. Waiting for main to finish."
    wait $MAIN_PID
  fi
else
  echo "No frontend directory found; waiting for main to finish."
  wait $MAIN_PID
fi
