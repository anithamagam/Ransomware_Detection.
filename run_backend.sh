#!/usr/bin/env bash
set -euo pipefail

# Build frontend (if using Vite) and run backend with uvicorn
ROOT_DIR=$(dirname "$0")
cd "$ROOT_DIR"

# Build frontend if frontend directory exists
if [ -d "frontend" ]; then
  echo "Building frontend..."
  cd frontend
  if [ -f package.json ]; then
    # prefer pnpm if available
    if command -v pnpm >/dev/null 2>&1; then
      pnpm install
      pnpm run build
    else
      npm install
      npm run build
    fi
  fi
  cd -
fi

# Start backend
echo "Starting backend API on http://127.0.0.1:8000"
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
