#!/bin/sh
set -e
python seed.py
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
