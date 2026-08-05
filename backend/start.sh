#!/usr/bin/env bash
# Start script to run health server and streamlit together
set -euo pipefail

# Start uvicorn health server in background binding only to localhost
uvicorn backend.app_health:app --host 127.0.0.1 --port 8000 --log-level warning &
HEALTH_PID=$!

# Ensure the health server is terminated when this script exits
trap "kill $HEALTH_PID" EXIT

# Start streamlit (foreground)
exec streamlit run app.py --server.port 8501 --server.address 0.0.0.0
