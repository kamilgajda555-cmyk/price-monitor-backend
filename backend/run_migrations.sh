#!/usr/bin/env bash
set -e

echo "=== Running Alembic migrations ==="
cd /app
# Use backend/alembic.ini so paths resolve
alembic -c backend/alembic.ini upgrade head
echo "=== Migrations complete ==="
