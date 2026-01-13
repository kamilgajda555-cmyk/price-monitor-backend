from celery import Celery
from celery.schedules import crontab
import os
from dotenv import load_dotenv

load_dotenv()

# Strip trailing slash from REDIS_URL (common misconfiguration)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0").rstrip('/')

celery_app = Celery(
    "price_monitor",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        'app.tasks.scraping_tasks', 
        'app.tasks.alert_tasks',
        'app.tasks.aggregation_tasks'  # Added aggregation tasks
    ]
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minutes (increased for large scraping jobs)
    task_soft_time_limit=540,  # 9 minutes
    worker_prefetch_multiplier=1,  # Don't prefetch tasks (better for long-running tasks)
    broker_connection_retry_on_startup=True,  # Suppress warnings
)

# Production-ready schedule
celery_app.conf.beat_schedule = {
    # Scraping: Daily at 2:00 AM UTC
    'scrape-all-products-daily': {
        'task': 'app.tasks.scraping_tasks.scrape_all_products',
        'schedule': crontab(hour=2, minute=0),
        'options': {'queue': 'scraping'},  # Dedicated queue
    },
    
    # Aggregation: Daily at 3:00 AM UTC (after scraping completes)
    'calculate-daily-stats': {
        'task': 'app.tasks.aggregation_tasks.calculate_daily_stats',
        'schedule': crontab(hour=3, minute=0),
        'options': {'queue': 'default'},
    },
    
    # Source stats: Daily at 3:30 AM UTC
    'calculate-source-stats': {
        'task': 'app.tasks.aggregation_tasks.calculate_source_stats',
        'schedule': crontab(hour=3, minute=30),
        'options': {'queue': 'default'},
    },
    
    # Price change calculation: Daily at 4:00 AM UTC
    'update-product-source-changes': {
        'task': 'app.tasks.aggregation_tasks.update_product_source_changes',
        'schedule': crontab(hour=4, minute=0),
        'options': {'queue': 'default'},
    },
    
    # Alerts: Every hour
    'check-alerts-hourly': {
        'task': 'app.tasks.alert_tasks.check_all_alerts',
        'schedule': crontab(minute=0),
        'options': {'queue': 'default'},
    },
    
    # Cleanup old data: Weekly on Sunday at 5:00 AM UTC
    'cleanup-old-price-history': {
        'task': 'app.tasks.aggregation_tasks.cleanup_old_data',
        'schedule': crontab(hour=5, minute=0, day_of_week=0),
        'options': {'queue': 'default'},
    },
}

# Task routing
celery_app.conf.task_routes = {
    'app.tasks.scraping_tasks.*': {'queue': 'scraping'},
    'app.tasks.aggregation_tasks.*': {'queue': 'default'},
    'app.tasks.alert_tasks.*': {'queue': 'default'},
}
