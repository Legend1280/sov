#!/bin/bash
# Start Core API (Semantic OS)

cd "$(dirname "$0")/../core"

echo "Starting Core API on port 8001..."
uvicorn api:app --reload --port 8001
