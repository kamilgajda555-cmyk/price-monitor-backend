#!/bin/bash
set -e

echo "=== Celery Worker Starting ==="
echo "Working dir: $(pwd)"
echo "Python: $(python --version)"

cd /app

# Uruchom Celery Worker bezpośrednio
exec celery -A app.tasks.celery_app worker \
    --loglevel=info \
    --concurrency=2 \
    --max-tasks-per-child=50
