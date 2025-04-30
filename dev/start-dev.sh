#!/bin/sh
set -e

echo "Starting FastAPI application"
exec poetry run uvicorn api.main:server --host 0.0.0.0 --port 8000 --workers 4 --reload
