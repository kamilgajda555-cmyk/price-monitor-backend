"""
Aggregation tasks for calculating daily statistics.
Runs after scraping completes to pre-calculate dashboard metrics.
"""
from app.tasks.celery_app import celery_app
from app.models.database import SessionLocal
from app.models.models import (
    Product, ProductSource, PriceHistory, 
    DailyPriceStats, SourceDailyStats
)
from sqlalchemy import func, and_
from datetime import datetime, timedelta, date
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@celery_app.task(name='app.tasks.aggregation_tasks.calculate_daily_stats')
def calculate_daily_stats(target_date: str = None):
    """
    Calculate daily price statistics for all products.
    Should run after daily scraping completes (e.g., 3 AM).
    
    Args:
        target_date: Date to calculate stats for (YYYY-MM-DD). Defaults to yesterday.
    """
    db = SessionLocal()
    
    try:
        # Parse target date or use yesterday
        if target_date:
            calc_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        else:
            calc_date = date.today() - timedelta(days=1)
        
        logger.info(f"Calculating daily stats for {calc_date}")
        
        # Get all active products
        products = db.query(Product).filter(Product.is_active == True).all()
        
        stats_created = 0
        stats_updated = 0
        
        for product in products:
            # Get price history for this date
            start_time = datetime.combine(calc_date, datetime.min.time())
            end_time = datetime.combine(calc_date, datetime.max.time())
            
            prices = db.query(PriceHistory).filter(
                and_(
                    PriceHistory.product_id == product.id,
                    PriceHistory.checked_at >= start_time,
                    PriceHistory.checked_at <= end_time
                )
            ).all()
            
            if not prices:
                continue
            
            # Calculate aggregates
            price_values = [float(p.price) for p in prices]
            available_sources = sum(1 for p in prices if p.availability)
            
            min_price = min(price_values)
            max_price = max(price_values)
            avg_price = sum(price_values) / len(price_values)
            median_price = sorted(price_values)[len(price_values) // 2]
            
            # Find best source
            best_price_record = min(prices, key=lambda p: float(p.price) if p.availability else float('inf'))
            
            # Get previous day stats for comparison
            prev_stats = db.query(DailyPriceStats).filter(
                and_(
                    DailyPriceStats.product_id == product.id,
                    DailyPriceStats.date == calc_date - timedelta(days=1)
                )
            ).first()
            
            change_from_previous = None
            change_percentage = None
            if prev_stats and prev_stats.avg_price:
                change_from_previous = avg_price - float(prev_stats.avg_price)
                change_percentage = (change_from_previous / float(prev_stats.avg_price)) * 100
            
            # Check if stats already exist
            existing_stats = db.query(DailyPriceStats).filter(
                and_(
                    DailyPriceStats.product_id == product.id,
                    DailyPriceStats.date == calc_date
                )
            ).first()
            
            if existing_stats:
                # Update existing
                existing_stats.min_price = min_price
                existing_stats.max_price = max_price
                existing_stats.avg_price = avg_price
                existing_stats.median_price = median_price
                existing_stats.sources_available = available_sources
                existing_stats.total_sources_checked = len(prices)
                existing_stats.best_source_id = best_price_record.source_id
                existing_stats.best_price = best_price_record.price
                existing_stats.change_from_previous = change_from_previous
                existing_stats.change_percentage = change_percentage
                stats_updated += 1
            else:
                # Create new
                daily_stats = DailyPriceStats(
                    product_id=product.id,
                    date=calc_date,
                    min_price=min_price,
                    max_price=max_price,
                    avg_price=avg_price,
                    median_price=median_price,
                    sources_available=available_sources,
                    total_sources_checked=len(prices),
                    best_source_id=best_price_record.source_id,
                    best_price=best_price_record.price,
                    change_from_previous=change_from_previous,
                    change_percentage=change_percentage
                )
                db.add(daily_stats)
                stats_created += 1
            
            # Update product cached stats
            product.min_price = min_price
            product.max_price = max_price
            product.avg_price = avg_price
            product.last_scraped = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Daily stats calculation completed: {stats_created} created, {stats_updated} updated")
        return {
            "status": "success",
            "date": str(calc_date),
            "stats_created": stats_created,
            "stats_updated": stats_updated
        }
        
    except Exception as e:
        logger.error(f"Error calculating daily stats: {e}")
        db.rollback()
        return {"status": "error", "error": str(e)}
    finally:
        db.close()


@celery_app.task(name='app.tasks.aggregation_tasks.calculate_source_stats')
def calculate_source_stats(target_date: str = None):
    """
    Calculate daily statistics per source.
    """
    db = SessionLocal()
    
    try:
        if target_date:
            calc_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        else:
            calc_date = date.today() - timedelta(days=1)
        
        logger.info(f"Calculating source stats for {calc_date}")
        
        from app.models.models import Source
        sources = db.query(Source).filter(Source.is_active == True).all()
        
        for source in sources:
            start_time = datetime.combine(calc_date, datetime.min.time())
            end_time = datetime.combine(calc_date, datetime.max.time())
            
            # Get all price records for this source today
            prices = db.query(PriceHistory).filter(
                and_(
                    PriceHistory.source_id == source.id,
                    PriceHistory.checked_at >= start_time,
                    PriceHistory.checked_at <= end_time
                )
            ).all()
            
            if not prices:
                continue
            
            successful_scrapes = len(prices)
            products_scraped = len(set(p.product_id for p in prices))
            products_unavailable = sum(1 for p in prices if not p.availability)
            
            # Calculate price changes
            price_changes = []
            for price in prices:
                # Get yesterday's price for same product
                yesterday = calc_date - timedelta(days=1)
                prev_price = db.query(PriceHistory).filter(
                    and_(
                        PriceHistory.product_id == price.product_id,
                        PriceHistory.source_id == price.source_id,
                        func.date(PriceHistory.checked_at) == yesterday
                    )
                ).first()
                
                if prev_price and prev_price.price:
                    change = ((float(price.price) - float(prev_price.price)) / float(prev_price.price)) * 100
                    price_changes.append(change)
            
            avg_price_change = sum(price_changes) / len(price_changes) if price_changes else 0
            products_price_increased = sum(1 for c in price_changes if c > 0)
            products_price_decreased = sum(1 for c in price_changes if c < 0)
            
            # Create or update stats
            existing_stats = db.query(SourceDailyStats).filter(
                and_(
                    SourceDailyStats.source_id == source.id,
                    SourceDailyStats.date == calc_date
                )
            ).first()
            
            if existing_stats:
                existing_stats.products_scraped = products_scraped
                existing_stats.successful_scrapes = successful_scrapes
                existing_stats.avg_price_change = avg_price_change
                existing_stats.products_price_increased = products_price_increased
                existing_stats.products_price_decreased = products_price_decreased
                existing_stats.products_unavailable = products_unavailable
            else:
                source_stats = SourceDailyStats(
                    source_id=source.id,
                    date=calc_date,
                    products_scraped=products_scraped,
                    successful_scrapes=successful_scrapes,
                    avg_price_change=avg_price_change,
                    products_price_increased=products_price_increased,
                    products_price_decreased=products_price_decreased,
                    products_unavailable=products_unavailable
                )
                db.add(source_stats)
        
        db.commit()
        logger.info(f"Source stats calculation completed for {calc_date}")
        return {"status": "success", "date": str(calc_date)}
        
    except Exception as e:
        logger.error(f"Error calculating source stats: {e}")
        db.rollback()
        return {"status": "error", "error": str(e)}
    finally:
        db.close()


@celery_app.task(name='app.tasks.aggregation_tasks.update_product_source_changes')
def update_product_source_changes():
    """
    Update price_change_1d, price_change_7d, price_change_30d in ProductSource.
    Run daily after scraping.
    """
    db = SessionLocal()
    
    try:
        logger.info("Updating product source price changes")
        
        product_sources = db.query(ProductSource).filter(
            ProductSource.is_active == True
        ).all()
        
        updated_count = 0
        
        for ps in product_sources:
            if not ps.last_price or not ps.last_checked:
                continue
            
            # Get historical prices
            price_1d = db.query(PriceHistory).filter(
                and_(
                    PriceHistory.product_id == ps.product_id,
                    PriceHistory.source_id == ps.source_id,
                    func.date(PriceHistory.checked_at) == date.today() - timedelta(days=1)
                )
            ).first()
            
            price_7d = db.query(PriceHistory).filter(
                and_(
                    PriceHistory.product_id == ps.product_id,
                    PriceHistory.source_id == ps.source_id,
                    func.date(PriceHistory.checked_at) == date.today() - timedelta(days=7)
                )
            ).first()
            
            price_30d = db.query(PriceHistory).filter(
                and_(
                    PriceHistory.product_id == ps.product_id,
                    PriceHistory.source_id == ps.source_id,
                    func.date(PriceHistory.checked_at) == date.today() - timedelta(days=30)
                )
            ).first()
            
            # Calculate changes
            if price_1d and price_1d.price:
                ps.price_change_1d = ((ps.last_price - float(price_1d.price)) / float(price_1d.price)) * 100
            
            if price_7d and price_7d.price:
                ps.price_change_7d = ((ps.last_price - float(price_7d.price)) / float(price_7d.price)) * 100
            
            if price_30d and price_30d.price:
                ps.price_change_30d = ((ps.last_price - float(price_30d.price)) / float(price_30d.price)) * 100
            
            updated_count += 1
        
        db.commit()
        logger.info(f"Updated price changes for {updated_count} product sources")
        return {"status": "success", "updated": updated_count}
        
    except Exception as e:
        logger.error(f"Error updating product source changes: {e}")
        db.rollback()
        return {"status": "error", "error": str(e)}
    finally:
        db.close()


@celery_app.task(name='app.tasks.aggregation_tasks.cleanup_old_data')
def cleanup_old_data(days_to_keep: int = 365):
    """
    Clean up old price history data to prevent database bloat.
    Keeps daily_price_stats forever, but removes raw price_history older than X days.
    
    Args:
        days_to_keep: Number of days of raw price history to keep (default 365)
    """
    db = SessionLocal()
    
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        logger.info(f"Cleaning up price history older than {cutoff_date}")
        
        # Delete old price history
        deleted_count = db.query(PriceHistory).filter(
            PriceHistory.checked_at < cutoff_date
        ).delete(synchronize_session=False)
        
        db.commit()
        
        logger.info(f"Deleted {deleted_count} old price history records")
        
        # Vacuum the table (PostgreSQL specific)
        # This should be done manually or via pg_cron
        
        return {
            "status": "success",
            "deleted_count": deleted_count,
            "cutoff_date": str(cutoff_date)
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up old data: {e}")
        db.rollback()
        return {"status": "error", "error": str(e)}
    finally:
        db.close()
