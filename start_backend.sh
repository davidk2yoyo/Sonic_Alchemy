#!/bin/bash
# Start backend with correct environment variables
cd "$(dirname "$0")/backend"
source ../venv/bin/activate
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5442
export MINIO_ENDPOINT=localhost:9010
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
