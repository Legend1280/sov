#!/bin/bash
# Start DexaBooks API

cd "$(dirname "$0")/../apps/dexabooks/backend"

echo "Starting DexaBooks API on port 8002..."
uvicorn api_finance:app --reload --port 8002
