#!/bin/bash
set -e

echo "=== Celery Beat Starting ==="
echo "Working dir: $(pwd)"
echo "Python: $(python --version)"

cd /app

# Uruchom Celery Beat bezpośrednio
exec celery -A app.tasks.celery_app beat \
    --loglevel=info
