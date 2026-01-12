from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.models.database import get_db
from app.models.models import Product, ProductSource, Source, ScrapeJob
from app.api.auth import get_current_user

router = APIRouter()

@router.post("/all")
def trigger_scrape_all(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Trigger scraping for all active products from all active sources.
    Uses Celery Worker for async processing.
    """
    try:
        from app.tasks.scraping_tasks import scrape_all_products
        
        # Queue the scraping task in Celery
        task = scrape_all_products.delay()
        
        return {
            "status": "queued",
            "message": "Scraping job has been queued in Celery",
            "task_id": task.id
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to queue scraping task: {str(e)}"
        )


@router.post("/product/{product_id}")
def trigger_scrape_product(
    product_id: int,
    source_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Trigger scraping for a specific product.
    If source_id is provided, scrape only from that source.
    Otherwise, scrape from all active sources for this product.
    """
    try:
        from app.tasks.scraping_tasks import scrape_product
        
        # Check if product exists
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        if source_id:
            # Scrape from specific source
            task = scrape_product.delay(product_id, source_id)
            return {
                "status": "queued",
                "message": f"Scraping product {product_id} from source {source_id}",
                "task_id": task.id
            }
        else:
            # Scrape from all sources
            product_sources = db.query(ProductSource).filter(
                ProductSource.product_id == product_id,
                ProductSource.is_active == True
            ).all()
            
            if not product_sources:
                raise HTTPException(
                    status_code=404, 
                    detail="No active sources found for this product"
                )
            
            tasks = []
            for ps in product_sources:
                task = scrape_product.delay(product_id, ps.source_id)
                tasks.append(task.id)
            
            return {
                "status": "queued",
                "message": f"Scraping product {product_id} from {len(tasks)} sources",
                "task_ids": tasks
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/source/{source_id}")
def trigger_scrape_source(
    source_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Trigger scraping for all products from a specific source.
    """
    try:
        from app.tasks.scraping_tasks import scrape_products_by_source
        
        # Check if source exists
        source = db.query(Source).filter(Source.id == source_id).first()
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")
        
        # Queue the task
        task = scrape_products_by_source.delay(source_id)
        
        return {
            "status": "queued",
            "message": f"Scraping all products from source {source.name}",
            "task_id": task.id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs")
def get_scrape_jobs(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get recent scraping jobs and their status.
    """
    jobs = db.query(ScrapeJob).order_by(ScrapeJob.started_at.desc()).limit(limit).all()
    
    return [
        {
            "id": job.id,
            "status": job.status,
            "started_at": job.started_at,
            "completed_at": job.completed_at,
            "prices_found": job.prices_found,
            "error_message": job.error_message
        }
        for job in jobs
    ]


@router.get("/status/{task_id}")
def get_scrape_status(
    task_id: str,
    current_user = Depends(get_current_user)
):
    """
    Get status of a specific Celery scraping task.
    """
    try:
        from app.tasks.celery_app import celery_app
        
        task = celery_app.AsyncResult(task_id)
        
        return {
            "task_id": task_id,
            "status": task.status,
            "result": task.result if task.ready() else None,
            "info": task.info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
def get_scraping_status(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get current scraping system status.
    """
    total_products = db.query(Product).filter(Product.is_active == True).count()
    total_sources = db.query(Source).filter(Source.is_active == True).count()
    total_mappings = db.query(ProductSource).filter(ProductSource.is_active == True).count()
    
    recent_job = db.query(ScrapeJob).order_by(ScrapeJob.started_at.desc()).first()
    
    return {
        "active_products": total_products,
        "active_sources": total_sources,
        "active_mappings": total_mappings,
        "last_scrape": recent_job.started_at if recent_job else None,
        "last_scrape_status": recent_job.status if recent_job else None,
        "celery_enabled": True
    }
