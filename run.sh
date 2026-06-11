#!/usr/bin/env bash
# PolicyFresh — local run script.
set -e
cd "$(dirname "$0")"
echo "Starting PolicyFresh on http://127.0.0.1:8000 ..."
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
