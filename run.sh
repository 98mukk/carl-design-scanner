#!/bin/bash
# CARL one-command setup + launch (Mac/Linux)
cd "$(dirname "$0")"

if [ ! -d .venv ]; then
  echo "Setting up CARL (first run only)..."
  python3 -m venv .venv
  .venv/bin/pip install -q -r requirements.txt
fi

if [ ! -f .env ]; then
  echo ""
  echo "CARL needs a Firecrawl API key (free at https://firecrawl.dev)."
  read -p "Paste your Firecrawl API key: " key
  echo "FIRECRAWL_API_KEY=$key" > .env
fi

echo "Starting CARL at http://127.0.0.1:8000 (Ctrl+C to stop)"
(sleep 1.5 && open http://127.0.0.1:8000 2>/dev/null) &
.venv/bin/uvicorn app:app --port 8000
