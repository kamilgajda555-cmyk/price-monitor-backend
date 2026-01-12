# Database Migrations

## Overview

This project uses Alembic for database migrations to safely evolve the schema as the application grows.

## Initial Setup

```bash
# Initialize Alembic (already done)
alembic init migrations

# Create first migration
alembic revision --autogenerate -m "Initial schema with optimizations"

# Apply migration
alembic upgrade head
```

## Creating New Migrations

```bash
# After changing models
alembic revision --autogenerate -m "Description of changes"

# Review the generated migration file in migrations/versions/
# Edit if needed

# Apply migration
alembic upgrade head
```

## Rollback

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade <revision_id>

# Rollback all
alembic downgrade base
```

## Production Deployment

```bash
# On Render/production, migrations run automatically via start script
python -c "from app.models.database import engine, Base; Base.metadata.create_all(bind=engine)"
```

## Key Optimizations

### 1. Indexes
- Composite indexes for common query patterns
- Covering indexes for read-heavy queries
- Unique indexes to prevent duplicates

### 2. Table Partitioning (PostgreSQL)
For `price_history` table with millions of records:

```sql
-- Create partitioned table (manual step for production)
CREATE TABLE price_history_partitioned (LIKE price_history INCLUDING ALL)
PARTITION BY RANGE (checked_at);

-- Create monthly partitions
CREATE TABLE price_history_2026_01 PARTITION OF price_history_partitioned
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

-- Automate partition creation with pg_cron or trigger
```

### 3. Aggregation Tables
- `daily_price_stats` - Pre-calculated daily aggregates
- `source_daily_stats` - Source performance metrics
- Updated via Celery periodic tasks

## Performance Tips

### Vacuum and Analyze
```sql
-- Run periodically on production
VACUUM ANALYZE price_history;
VACUUM ANALYZE daily_price_stats;
```

### Check Index Usage
```sql
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;
```

### Monitor Table Sizes
```sql
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```
