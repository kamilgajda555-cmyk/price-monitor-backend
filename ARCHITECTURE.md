# Price Monitor - Production Architecture

## Overview

Production-grade price monitoring system designed for **10,000 products** across **20 sources** with **daily scraping** = **~9 million price records per year**.

---

## 📊 Scale & Performance

### Data Volume
- **10,000 products**
- **20 sources** (Allegro, Amazon, Empik, distributors)
- **~2.5 sources per product** average
- **25,000 price checks/day**
- **9,125,000 records/year** in `price_history`

### Performance Goals
- Dashboard load: **< 500ms**
- Price history query: **< 1s**
- Histogram generation: **< 2s**
- Scraping throughput: **100 products/minute**

---

## 🏗️ Database Schema

### Core Tables

#### `products`
- Primary product catalog
- Indexed: `sku`, `ean`, `category`, `brand`, `is_active`
- **Cached stats** for fast queries: `min_price`, `max_price`, `avg_price`

####  `sources`
- Source platforms (Allegro, Amazon, etc.)
- Scraper configuration (CSS selectors, API endpoints)
- Performance tracking

#### `product_sources`
- Many-to-many mapping
- **Composite indexes** for fast lookups
- **Price change cache**: 1d, 7d, 30d percentage changes

#### `price_history` ⚠️ **HIGH VOLUME**
- Raw price data (9M records/year)
- **Partitioned by date** (monthly partitions for PostgreSQL)
- **Composite indexes**: (product_id, checked_at), (product_id, source_id, checked_at)
- **Cleanup policy**: Keep last 365 days, delete older

### Aggregation Tables (Performance Optimization)

#### `daily_price_stats` ✅ **FAST QUERIES**
- Pre-calculated daily aggregates per product
- Only **3.65M records/year** (vs 9M in raw data)
- **Used by**: Dashboards, histograms, trends
- **Columns**: min/max/avg/median prices, changes, best source
- **Updated**: Daily at 3:00 AM by Celery Beat

#### `source_daily_stats`
- Source performance metrics
- Success rates, avg response time
- Price change trends per source

---

## ⚡ Performance Optimizations

### 1. Indexing Strategy

**Composite Indexes**:
```sql
-- Product source lookups (most common query)
CREATE INDEX idx_product_source_active 
ON product_sources(product_id, source_id, is_active);

-- Price history by date (for charts)
CREATE INDEX idx_price_product_date 
ON price_history(product_id, checked_at);

-- Daily stats (dashboard queries)
CREATE INDEX idx_daily_stats_product_date 
ON daily_price_stats(product_id, date);
```

### 2. Table Partitioning

**price_history partitioned by month**:
```sql
-- Example for PostgreSQL 12+
CREATE TABLE price_history_partitioned (
  LIKE price_history INCLUDING ALL
) PARTITION BY RANGE (checked_at);

-- Create monthly partitions
CREATE TABLE price_history_2026_01 PARTITION OF price_history_partitioned
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
```

**Benefits**:
- Faster queries (scan only relevant partitions)
- Easy data archival (drop old partitions)
- Better vacuum performance

### 3. Aggregation Strategy

**Daily Celery tasks** (run after scraping):
1. `calculate_daily_stats` - Pre-calc product aggregates
2. `calculate_source_stats` - Source performance
3. `update_product_source_changes` - Rolling change percentages

**Result**: Dashboard queries hit 3.65M aggregated records instead of 9M raw records = **2.5x faster**

### 4. Caching

**Application-level cache**:
```python
# Product table stores cached stats
product.min_price  # Updated after each scrape
product.max_price
product.avg_price
product.last_scraped
```

**ProductSource change cache**:
```python
product_source.price_change_1d   # % change from yesterday
product_source.price_change_7d   # % change from 7 days ago
product_source.price_change_30d  # % change from 30 days ago
```

---

## 🔄 Data Flow

### Scraping Flow
```
Celery Beat (2:00 AM)
    ↓
scrape_all_products task
    ↓
Queue individual scrape_product tasks
    ↓
Celery Worker (concurrency=2)
    ↓
Playwright → Scraper → Parse price
    ↓
Save to price_history
    ↓
Update product_sources.last_price
```

### Aggregation Flow
```
Celery Beat (3:00 AM)
    ↓
calculate_daily_stats task
    ↓
Query price_history for yesterday
    ↓
Calculate min/max/avg/median per product
    ↓
Save to daily_price_stats
    ↓
Update product cached stats
```

### Query Flow (Dashboard)
```
Frontend → GET /analytics/dashboard/overview
    ↓
Query daily_price_stats (fast!)
    ↓
Calculate trends from aggregates
    ↓
Return JSON
```

---

## 📈 API Endpoints

### Analytics (New!)

#### Histogram
```http
GET /api/v1/analytics/product/{id}/price-histogram?days=30
```
**Returns**: Daily min/max/avg prices for charts

#### Price Changes
```http
GET /api/v1/analytics/product/{id}/price-changes?days=7
```
**Returns**: Day-to-day percentage changes

#### Source Comparison
```http
GET /api/v1/analytics/product/{id}/source-comparison
```
**Returns**: Current prices across all sources, sorted by price

#### Dashboard Overview
```http
GET /api/v1/analytics/dashboard/overview?days=7
```
**Returns**:
- Total products/sources
- Price checks last 24h
- Biggest price drops/increases
- Products with price changes

#### Source Performance
```http
GET /api/v1/analytics/source/{id}/performance?days=30
```
**Returns**: Success rates, response times, price trends

---

## 🕐 Celery Schedule

### Daily Schedule (UTC)
```
02:00 - Scrape all products (primary job)
03:00 - Calculate daily price stats
03:30 - Calculate source performance stats
04:00 - Update product source price changes
05:00 - Cleanup old data (Sunday only)

Every hour - Check price alerts
```

### Task Queues
```
scraping queue:
  - scrape_all_products
  - scrape_product
  - scrape_products_by_source

default queue:
  - aggregation tasks
  - alert tasks
```

---

## 💾 Data Retention Policy

### price_history (raw data)
- **Keep**: Last 365 days
- **Delete**: Older than 365 days
- **Why**: Aggregated stats kept forever in daily_price_stats

### daily_price_stats (aggregated)
- **Keep**: Forever
- **Size**: ~10 MB/year (vs 1+ GB for raw data)

### scrape_jobs (logs)
- **Keep**: Last 90 days
- **Delete**: Older logs

---

## 🔍 Monitoring Queries

### Check database size
```sql
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Check index usage
```sql
SELECT
    schemaname || '.' || tablename AS table,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE idx_scan = 0  -- Unused indexes
ORDER BY pg_relation_size(indexrelid) DESC;
```

### Check slow queries (PostgreSQL)
```sql
SELECT
    query,
    calls,
    total_time,
    mean_time,
    max_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 20;
```

---

## 🚀 Scaling Strategy

### Vertical Scaling
- **Celery Worker**: Upgrade from $7/month to $14/month (1GB RAM)
- **Database**: Upgrade to Standard plan ($7/month) for 10GB storage

### Horizontal Scaling
- **Add Celery Workers**: $7/month each
  - 2 workers = 2x throughput
  - 4 workers = 4x throughput
- **Dedicated scraping queue**: Separate workers for scraping vs aggregation

### Database Optimization
- **Read replicas**: For analytics queries
- **Connection pooling**: pgBouncer
- **Caching layer**: Redis for frequently accessed data

---

## 📊 Expected Performance

### With Current Architecture

| Metric | Value |
|--------|-------|
| Products scraped/day | 10,000 |
| Time to scrape all | ~100 minutes |
| Database size (1 year) | ~2-3 GB |
| Dashboard load time | < 500ms |
| Histogram query | < 1s |
| API response time (p95) | < 200ms |

### Bottlenecks

1. **Scraping speed**: Limited by Playwright + network
   - **Solution**: More workers, rate limiting per source
2. **Database writes**: 25k inserts/day
   - **Solution**: Batch inserts, connection pooling
3. **Aggregation time**: Processing 25k records
   - **Solution**: Parallel processing, incremental updates

---

## 🛡️ Best Practices

### Scraping
1. **Rate limiting**: Max 1 request/2 seconds per source
2. **Retry logic**: 3 attempts with exponential backoff
3. **Timeout**: 30 seconds per product
4. **User agent rotation**: Avoid bot detection
5. **Error handling**: Log failures, don't block pipeline

### Database
1. **Use Numeric** for prices (not Float) - exact precision
2. **Index foreign keys** - essential for joins
3. **Regular VACUUM** - prevent bloat
4. **Monitor query performance** - pg_stat_statements
5. **Backup strategy** - Daily automated backups

### Celery
1. **Task idempotency** - tasks can be safely retried
2. **Result expiration** - Clear old task results
3. **Worker monitoring** - Track task success/failure rates
4. **Memory limits** - Prevent worker OOM
5. **Graceful shutdown** - Finish current task before stopping

---

## 🔧 Maintenance Tasks

### Daily (Automated)
- Scrape products
- Calculate aggregates
- Check alerts
- Backup database

### Weekly (Automated)
- Cleanup old price_history
- Vacuum database tables

### Monthly (Manual)
- Review slow queries
- Check index usage
- Analyze scraper success rates
- Review storage growth

### Quarterly (Manual)
- Update scraper selectors (sites change layout)
- Review and optimize indexes
- Database performance tuning
- Cost optimization review

---

This architecture is **production-ready** for 10k products × 20 sources with room to scale to 100k products.
