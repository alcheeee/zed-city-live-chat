#!/bin/bash
set -e

# Start FastAPI
exec poetry run uvicorn api.main:server --host 0.0.0.0 --port 8000 --workers 4
