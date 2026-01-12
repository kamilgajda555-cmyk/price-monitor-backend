"""
Analytics API endpoints for price statistics, histograms, and trends.
Optimized for large-scale data (10k products × 20 sources).
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from typing import List, Optional
from datetime import datetime, timedelta, date

from app.models.database import get_db
from app.models.models import (
    Product, ProductSource, PriceHistory, 
    DailyPriceStats, SourceDailyStats
)
from app.api.auth import get_current_user

router = APIRouter()

@router.get("/product/{product_id}/price-histogram")
def get_price_histogram(
    product_id: int,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get price histogram for a product over time.
    Uses pre-calculated daily_price_stats for fast queries.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get daily stats (fast query on aggregated data)
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    daily_stats = db.query(DailyPriceStats).filter(
        and_(
            DailyPriceStats.product_id == product_id,
            DailyPriceStats.date >= start_date,
            DailyPriceStats.date <= end_date
        )
    ).order_by(DailyPriceStats.date).all()
    
    return {
        "product_id": product_id,
        "product_name": product.name,
        "period_days": days,
        "data": [
            {
                "date": str(stat.date),
                "min_price": float(stat.min_price) if stat.min_price else None,
                "max_price": float(stat.max_price) if stat.max_price else None,
                "avg_price": float(stat.avg_price) if stat.avg_price else None,
                "median_price": float(stat.median_price) if stat.median_price else None,
                "change_percentage": stat.change_percentage,
                "sources_available": stat.sources_available,
                "best_price": float(stat.best_price) if stat.best_price else None,
            }
            for stat in daily_stats
        ]
    }


@router.get("/product/{product_id}/price-changes")
def get_price_changes(
    product_id: int,
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get day-to-day price changes for analysis.
    Returns absolute and percentage changes.
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    daily_stats = db.query(DailyPriceStats).filter(
        and_(
            DailyPriceStats.product_id == product_id,
            DailyPriceStats.date >= start_date,
            DailyPriceStats.date <= end_date
        )
    ).order_by(DailyPriceStats.date).all()
    
    changes = []
    for i in range(1, len(daily_stats)):
        prev = daily_stats[i-1]
        curr = daily_stats[i]
        
        if prev.avg_price and curr.avg_price:
            abs_change = float(curr.avg_price) - float(prev.avg_price)
            pct_change = (abs_change / float(prev.avg_price)) * 100
            
            changes.append({
                "date": str(curr.date),
                "previous_price": float(prev.avg_price),
                "current_price": float(curr.avg_price),
                "absolute_change": round(abs_change, 2),
                "percentage_change": round(pct_change, 2),
                "trend": "up" if abs_change > 0 else "down" if abs_change < 0 else "stable"
            })
    
    return {
        "product_id": product_id,
        "period_days": days,
        "changes": changes
    }


@router.get("/product/{product_id}/source-comparison")
def get_source_comparison(
    product_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Compare prices across all sources for a product.
    Shows current prices and 7-day trends.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get all product sources with current prices
    product_sources = db.query(ProductSource).filter(
        and_(
            ProductSource.product_id == product_id,
            ProductSource.is_active == True
        )
    ).all()
    
    comparison = []
    for ps in product_sources:
        # Get source info
        from app.models.models import Source
        source = db.query(Source).filter(Source.id == ps.source_id).first()
        
        comparison.append({
            "source_id": ps.source_id,
            "source_name": source.name if source else "Unknown",
            "current_price": ps.last_price,
            "availability": ps.last_availability,
            "last_checked": ps.last_checked,
            "price_change_1d": ps.price_change_1d,
            "price_change_7d": ps.price_change_7d,
            "price_change_30d": ps.price_change_30d,
            "url": ps.source_url
        })
    
    # Sort by price (cheapest first)
    comparison.sort(key=lambda x: x['current_price'] if x['current_price'] else float('inf'))
    
    return {
        "product_id": product_id,
        "product_name": product.name,
        "sources": comparison,
        "best_price": comparison[0]['current_price'] if comparison else None,
        "price_spread": (comparison[-1]['current_price'] - comparison[0]['current_price']) if len(comparison) > 1 and comparison[0]['current_price'] and comparison[-1]['current_price'] else None
    }


@router.get("/dashboard/overview")
def get_dashboard_overview(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get comprehensive dashboard overview.
    Optimized for large datasets.
    """
    # Product stats
    total_products = db.query(func.count(Product.id)).filter(Product.is_active == True).scalar()
    
    # Source stats
    total_sources = db.query(func.count(ProductSource.id)).filter(
        ProductSource.is_active == True
    ).scalar()
    
    # Recent price checks (from last 24 hours)
    yesterday = datetime.utcnow() - timedelta(days=1)
    recent_checks = db.query(func.count(PriceHistory.id)).filter(
        PriceHistory.checked_at >= yesterday
    ).scalar()
    
    # Price trends (from daily_price_stats)
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    # Products with price drops
    products_price_dropped = db.query(func.count(DailyPriceStats.id)).filter(
        and_(
            DailyPriceStats.date == end_date - timedelta(days=1),
            DailyPriceStats.change_percentage < 0
        )
    ).scalar()
    
    # Products with price increases
    products_price_increased = db.query(func.count(DailyPriceStats.id)).filter(
        and_(
            DailyPriceStats.date == end_date - timedelta(days=1),
            DailyPriceStats.change_percentage > 0
        )
    ).scalar()
    
    # Biggest price drops (last 7 days)
    biggest_drops = db.query(
        DailyPriceStats, Product
    ).join(Product).filter(
        and_(
            DailyPriceStats.date >= start_date,
            DailyPriceStats.change_percentage < 0
        )
    ).order_by(DailyPriceStats.change_percentage).limit(10).all()
    
    # Biggest price increases (last 7 days)
    biggest_increases = db.query(
        DailyPriceStats, Product
    ).join(Product).filter(
        and_(
            DailyPriceStats.date >= start_date,
            DailyPriceStats.change_percentage > 0
        )
    ).order_by(desc(DailyPriceStats.change_percentage)).limit(10).all()
    
    return {
        "overview": {
            "total_products": total_products,
            "total_sources": total_sources,
            "price_checks_24h": recent_checks,
            "products_price_dropped": products_price_dropped,
            "products_price_increased": products_price_increased,
        },
        "biggest_drops": [
            {
                "product_id": stat.product_id,
                "product_name": product.name,
                "date": str(stat.date),
                "change_percentage": stat.change_percentage,
                "previous_price": float(stat.avg_price - stat.change_from_previous) if stat.change_from_previous else None,
                "current_price": float(stat.avg_price) if stat.avg_price else None,
            }
            for stat, product in biggest_drops
        ],
        "biggest_increases": [
            {
                "product_id": stat.product_id,
                "product_name": product.name,
                "date": str(stat.date),
                "change_percentage": stat.change_percentage,
                "previous_price": float(stat.avg_price - stat.change_from_previous) if stat.change_from_previous else None,
                "current_price": float(stat.avg_price) if stat.avg_price else None,
            }
            for stat, product in biggest_increases
        ]
    }


@router.get("/source/{source_id}/performance")
def get_source_performance(
    source_id: int,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get source performance metrics over time.
    """
    from app.models.models import Source
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    daily_stats = db.query(SourceDailyStats).filter(
        and_(
            SourceDailyStats.source_id == source_id,
            SourceDailyStats.date >= start_date,
            SourceDailyStats.date <= end_date
        )
    ).order_by(SourceDailyStats.date).all()
    
    return {
        "source_id": source_id,
        "source_name": source.name,
        "period_days": days,
        "performance": [
            {
                "date": str(stat.date),
                "products_scraped": stat.products_scraped,
                "successful_scrapes": stat.successful_scrapes,
                "failed_scrapes": stat.failed_scrapes,
                "success_rate": (stat.successful_scrapes / (stat.successful_scrapes + stat.failed_scrapes) * 100) if (stat.successful_scrapes + stat.failed_scrapes) > 0 else 0,
                "avg_price_change": stat.avg_price_change,
                "products_unavailable": stat.products_unavailable,
            }
            for stat in daily_stats
        ]
    }
