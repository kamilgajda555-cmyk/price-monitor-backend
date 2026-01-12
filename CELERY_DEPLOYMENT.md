# Celery Worker Deployment Guide

## Overview

This application uses Celery for asynchronous task processing (web scraping).

**Architecture:**
- Backend (Web Service) - FastAPI - FREE tier
- Celery Worker (Background Worker) - Task processing - $7/month
- Celery Beat (Background Worker) - Scheduler - FREE tier (optional)
- Redis (Upstash) - Message broker - FREE tier

## Prerequisites

1. ✅ Render account with payment method added
2. ✅ Redis URL from Upstash (already configured)
3. ✅ GitHub repository pushed

## Deployment Steps

### 1. Create Celery Worker Service

**In Render Dashboard:**

1. Click **"New +"** → **Background Worker**

2. **Connect Repository:**
   - Repository: `kamilgajda555-cmyk/price-monitor-backend`
   - Branch: `main`

3. **Service Configuration:**
   ```
   Name: price-monitor-celery-worker
   Region: Frankfurt (EU Central)
   Branch: main
   Root Directory: backend
   Runtime: Docker
   Dockerfile Path: Dockerfile
   ```

4. **Docker Command:**
   ```bash
   bash start-celery-worker.sh
   ```

5. **Environment Variables** (copy from backend service):
   ```
   DATABASE_URL=postgresql://priceuser:Ff0r3LcM34rXLiTJEugLBYev7wPjTheN@dpg-d5hrruq4d50c73am0org-a/pricedb_dy6a
   REDIS_URL=redis://default:AReeAAImcDFkYzk3MjA2YTZlMGE0YzU0YTRlMmRjNWViNWM0ZGZlN3AxNjA0Ng@pleasing-halibut-6046.upstash.io:6379
   SECRET_KEY=4aQS8udEOX8crr6WdXVInHUvOF-z6B9qB1rT_Vj4CsA
   SCRAPING_TIMEOUT=30
   SCRAPING_DELAY=2
   USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
   ```

6. **Instance Type:**
   ```
   Starter ($7/month) - 512 MB RAM
   ```

7. Click **"Create Background Worker"**

---

### 2. Create Celery Beat Service (Optional - for automatic scheduling)

**In Render Dashboard:**

1. Click **"New +"** → **Background Worker**

2. **Service Configuration:**
   ```
   Name: price-monitor-celery-beat
   Region: Frankfurt (EU Central)
   Branch: main
   Root Directory: backend
   Runtime: Docker
   Dockerfile Path: Dockerfile
   ```

3. **Docker Command:**
   ```bash
   bash start-celery-beat.sh
   ```

4. **Environment Variables:** (same as Worker)

5. **Instance Type:**
   ```
   Free (512 MB RAM) - works fine for scheduler
   ```

6. Click **"Create Background Worker"**

---

## Testing

### 1. Check Celery Worker Logs

```
Render Dashboard → price-monitor-celery-worker → Logs
```

**Expected output:**
```
✅ Redis connected!
Starting Celery Worker...
[tasks]
  . app.tasks.scraping_tasks.scrape_all_products
  . app.tasks.scraping_tasks.scrape_product
  . app.tasks.scraping_tasks.scrape_products_by_source
celery@... ready.
```

### 2. Check Celery Beat Logs (if deployed)

```
Render Dashboard → price-monitor-celery-beat → Logs
```

**Expected output:**
```
✅ Redis connected!
Starting Celery Beat...
Schedule: Daily scraping at 2:00 AM UTC
beat: Starting...
```

### 3. Test Scraping via API

**Open application:**
```
https://quiet-gecko-10db7b.netlify.app
```

**Click: "🚀 Start Scraping"**

**Expected response:**
```json
{
  "status": "queued",
  "message": "Scraping job has been queued in Celery",
  "task_id": "abc-123-xyz-456"
}
```

### 4. Check Task Status

**API endpoint:**
```
GET /api/v1/scrape/status/{task_id}
```

**Response:**
```json
{
  "task_id": "abc-123-xyz-456",
  "status": "SUCCESS",
  "result": {
    "status": "completed",
    "successful": 5,
    "failed": 0,
    "total": 5
  }
}
```

---

## Troubleshooting

### Worker shows "Cannot connect to Redis"

**Check:**
1. REDIS_URL is correct in environment variables
2. Redis service is running (check Upstash dashboard)
3. Network connectivity from Render to Upstash

**Fix:**
- Re-enter REDIS_URL environment variable
- Restart worker service

### Worker shows "Out of memory"

**Solution:**
- Upgrade to Starter Plus ($14/month) for 1 GB RAM
- Or reduce concurrency in start-celery-worker.sh:
  ```bash
  --concurrency=1
  ```

### Tasks stuck in "PENDING"

**Check:**
1. Celery Worker is running (check logs)
2. Redis connection is working
3. Task is queued in correct queue

**Fix:**
```bash
# In Celery Worker logs, check:
[queues]
  .> celery  exchange=celery(direct) key=celery
```

---

## Monitoring

### Check active tasks

**Celery Worker logs:**
```
[2026-01-12 18:00:00] Received task: app.tasks.scraping_tasks.scrape_all_products
[2026-01-12 18:00:05] Task app.tasks.scraping_tasks.scrape_all_products succeeded
```

### Check scraping jobs

**API endpoint:**
```
GET /api/v1/scrape/jobs
```

**Response:**
```json
[
  {
    "id": 1,
    "status": "completed",
    "started_at": "2026-01-12T18:00:00",
    "completed_at": "2026-01-12T18:00:10",
    "prices_found": 5,
    "error_message": null
  }
]
```

---

## Cost Breakdown

| Service | Type | Cost |
|---------|------|------|
| Backend | Web Service | FREE |
| Celery Worker | Background Worker | $7/month |
| Celery Beat | Background Worker | FREE (optional) |
| PostgreSQL | Database | FREE |
| Redis (Upstash) | Message Broker | FREE |
| Frontend (Netlify) | Static Site | FREE |
| **TOTAL** | | **$7/month** |

---

## Scaling

### To handle more products:

**Upgrade Celery Worker:**
- Starter Plus ($14/month) - 1 GB RAM
- Standard ($25/month) - 2 GB RAM

**Or add more workers:**
- Create second Celery Worker service
- Both will process tasks from same Redis queue
- Cost: $7/month per additional worker

---

## Next Steps After Deployment

1. ✅ Add products via frontend
2. ✅ Add sources (Allegro, Amazon, Empik)
3. ✅ Connect products to sources
4. ✅ Click "Start Scraping" to test
5. ✅ Check Price History after scraping
6. ✅ Set up price alerts

---

## Support

If you encounter issues:

1. Check Render logs for all services
2. Verify environment variables are set correctly
3. Test Redis connection manually
4. Check GitHub repo is up to date

**Common issues:**
- Payment method required for Background Workers
- REDIS_URL must include password and use TLS
- Dockerfile must be in `backend/` directory
