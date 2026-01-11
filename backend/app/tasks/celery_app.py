from celery import Celery
from celery.schedules import crontab
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "price_monitor",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=['app.tasks.scraping_tasks', 'app.tasks.alert_tasks']
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
)

# Schedule: Run daily at 2 AM
celery_app.conf.beat_schedule = {
    'scrape-all-products-daily': {
        'task': 'app.tasks.scraping_tasks.scrape_all_products',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    'check-alerts-hourly': {
        'task': 'app.tasks.alert_tasks.check_all_alerts',
        'schedule': crontab(minute=0),  # Every hour
    },
}
