#!/usr/bin/env bash
set -e

echo "Initializing database..."
/venv/bin/python src/scripts/init_database.py

echo "Starting main application..."
exec "$@"
