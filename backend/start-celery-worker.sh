#!/bin/bash
set -e

echo "=== Starting Celery Worker ==="
echo "Redis URL: ${REDIS_URL:0:30}..."

# Wait for Redis to be available
echo "Checking Redis connection..."
python -c "
import os
import redis
import time

max_retries = 30
retry = 0

while retry < max_retries:
    try:
        r = redis.from_url(os.getenv('REDIS_URL'))
        r.ping()
        print('✅ Redis connected!')
        break
    except Exception as e:
        retry += 1
        print(f'⚠️  Redis not available yet ({retry}/{max_retries}): {e}')
        if retry < max_retries:
            time.sleep(2)
        else:
            print('❌ Failed to connect to Redis after 30 retries')
            exit(1)
"

# Start Celery Worker
echo "Starting Celery Worker..."
exec celery -A app.tasks.celery_app worker \
    --loglevel=info \
    --concurrency=2 \
    --max-tasks-per-child=50 \
    --time-limit=300 \
    --soft-time-limit=240
