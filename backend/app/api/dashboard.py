from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import List

from app.models.database import get_db
from app.models.models import Product, Source, PriceHistory, ScrapeJob
from app.schemas.schemas import DashboardStats, PriceAlert
from app.api.auth import get_current_user

router = APIRouter()

@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Total and active products
    total_products = db.query(func.count(Product.id)).scalar()
    active_products = db.query(func.count(Product.id)).filter(Product.is_active == True).scalar()
    
    # Total and active sources
    total_sources = db.query(func.count(Source.id)).scalar()
    active_sources = db.query(func.count(Source.id)).filter(Source.is_active == True).scalar()
    
    # Price checks today
    today = datetime.utcnow().date()
    price_checks_today = db.query(func.count(PriceHistory.id)).filter(
        func.date(PriceHistory.checked_at) == today
    ).scalar()
    
    # Products with price changes (simplified - compare today vs yesterday)
    yesterday = today - timedelta(days=1)
    
    # This is a simplified calculation - in production you'd want more sophisticated logic
    products_with_price_drop = 0
    products_with_price_increase = 0
    
    # Get average price change
    average_price_change = 0.0
    
    return DashboardStats(
        total_products=total_products or 0,
        active_products=active_products or 0,
        total_sources=total_sources or 0,
        active_sources=active_sources or 0,
        total_price_checks_today=price_checks_today or 0,
        products_with_price_drop=products_with_price_drop,
        products_with_price_increase=products_with_price_increase,
        average_price_change=average_price_change
    )

@router.get("/recent-alerts", response_model=List[PriceAlert])
def get_recent_alerts(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Get recent significant price changes
    # This is a simplified version - you'd want to track actual alerts
    recent_changes = []
    
    # Query for products with recent price changes
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    products = db.query(Product).filter(Product.is_active == True).limit(limit).all()
    
    for product in products:
        # Get latest and previous price for comparison
        latest_prices = db.query(PriceHistory).filter(
            PriceHistory.product_id == product.id,
            PriceHistory.checked_at >= seven_days_ago
        ).order_by(PriceHistory.checked_at.desc()).limit(2).all()
        
        if len(latest_prices) >= 2:
            new_price = latest_prices[0].price
            old_price = latest_prices[1].price
            change_percent = ((new_price - old_price) / old_price) * 100 if old_price > 0 else 0
            
            if abs(change_percent) > 5:  # Only show changes > 5%
                source = db.query(Source).filter(Source.id == latest_prices[0].source_id).first()
                recent_changes.append(PriceAlert(
                    product_id=product.id,
                    product_name=product.name,
                    source_name=source.name if source else "Unknown",
                    old_price=old_price,
                    new_price=new_price,
                    change_percent=round(change_percent, 2),
                    checked_at=latest_prices[0].checked_at
                ))
    
    return recent_changes[:limit]

@router.get("/scraping-status")
def get_scraping_status(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Get recent scraping jobs
    recent_jobs = db.query(ScrapeJob).order_by(ScrapeJob.created_at.desc()).limit(10).all()
    
    # Count by status
    total_jobs = db.query(func.count(ScrapeJob.id)).scalar()
    completed_jobs = db.query(func.count(ScrapeJob.id)).filter(ScrapeJob.status == "completed").scalar()
    failed_jobs = db.query(func.count(ScrapeJob.id)).filter(ScrapeJob.status == "failed").scalar()
    running_jobs = db.query(func.count(ScrapeJob.id)).filter(ScrapeJob.status == "running").scalar()
    
    return {
        "total_jobs": total_jobs or 0,
        "completed": completed_jobs or 0,
        "failed": failed_jobs or 0,
        "running": running_jobs or 0,
        "recent_jobs": [
            {
                "id": job.id,
                "status": job.status,
                "started_at": job.started_at,
                "completed_at": job.completed_at,
                "prices_found": job.prices_found,
                "error_message": job.error_message
            }
            for job in recent_jobs
        ]
    }
