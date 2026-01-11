from app.tasks.celery_app import celery_app
from app.models.database import SessionLocal
from app.models.models import Alert, Product, PriceHistory, Source
from app.services.email_service import send_alert_email
from datetime import datetime, timedelta
from sqlalchemy import desc
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@celery_app.task(name='app.tasks.alert_tasks.check_alert')
def check_alert(alert_id: int):
    """Check a single alert and send email if triggered"""
    db = SessionLocal()
    
    try:
        alert = db.query(Alert).filter(
            Alert.id == alert_id,
            Alert.is_active == True
        ).first()
        
        if not alert:
            return {"status": "skipped", "reason": "Alert not found or inactive"}
        
        # Get product
        product = db.query(Product).filter(Product.id == alert.product_id).first()
        if not product:
            return {"status": "skipped", "reason": "Product not found"}
        
        # Check alert type and condition
        triggered = False
        message = ""
        
        if alert.alert_type == "price_drop":
            triggered, message = _check_price_drop(db, alert, product)
        elif alert.alert_type == "price_increase":
            triggered, message = _check_price_increase(db, alert, product)
        elif alert.alert_type == "availability":
            triggered, message = _check_availability(db, alert, product)
        elif alert.alert_type == "competitor":
            triggered, message = _check_competitor_price(db, alert, product)
        
        if triggered:
            # Send email alert
            user_email = alert.user.email if hasattr(alert, 'user') else None
            if user_email:
                send_alert_email(user_email, product.name, message)
            
            # Update alert
            alert.last_triggered = datetime.utcnow()
            db.commit()
            
            logger.info(f"Alert {alert_id} triggered: {message}")
            return {"status": "triggered", "message": message}
        
        return {"status": "not_triggered"}
        
    except Exception as e:
        logger.error(f"Error checking alert {alert_id}: {e}")
        return {"status": "error", "error": str(e)}
    finally:
        db.close()

def _check_price_drop(db, alert: Alert, product: Product):
    """Check if price dropped below threshold"""
    threshold = alert.condition.get("threshold")
    percentage = alert.condition.get("percentage")
    
    # Get latest price
    latest_price = db.query(PriceHistory).filter(
        PriceHistory.product_id == product.id
    ).order_by(desc(PriceHistory.checked_at)).first()
    
    if not latest_price:
        return False, ""
    
    # Get previous price (24 hours ago)
    yesterday = datetime.utcnow() - timedelta(days=1)
    previous_price = db.query(PriceHistory).filter(
        PriceHistory.product_id == product.id,
        PriceHistory.checked_at <= yesterday
    ).order_by(desc(PriceHistory.checked_at)).first()
    
    if not previous_price:
        return False, ""
    
    # Check threshold
    if threshold and latest_price.price < threshold:
        return True, f"Price dropped to {latest_price.price} PLN (threshold: {threshold} PLN)"
    
    # Check percentage
    if percentage:
        price_change = ((latest_price.price - previous_price.price) / previous_price.price) * 100
        if price_change <= -percentage:
            return True, f"Price dropped by {abs(price_change):.2f}% to {latest_price.price} PLN"
    
    return False, ""

def _check_price_increase(db, alert: Alert, product: Product):
    """Check if price increased above threshold"""
    threshold = alert.condition.get("threshold")
    percentage = alert.condition.get("percentage")
    
    latest_price = db.query(PriceHistory).filter(
        PriceHistory.product_id == product.id
    ).order_by(desc(PriceHistory.checked_at)).first()
    
    if not latest_price:
        return False, ""
    
    yesterday = datetime.utcnow() - timedelta(days=1)
    previous_price = db.query(PriceHistory).filter(
        PriceHistory.product_id == product.id,
        PriceHistory.checked_at <= yesterday
    ).order_by(desc(PriceHistory.checked_at)).first()
    
    if not previous_price:
        return False, ""
    
    if threshold and latest_price.price > threshold:
        return True, f"Price increased to {latest_price.price} PLN (threshold: {threshold} PLN)"
    
    if percentage:
        price_change = ((latest_price.price - previous_price.price) / previous_price.price) * 100
        if price_change >= percentage:
            return True, f"Price increased by {price_change:.2f}% to {latest_price.price} PLN"
    
    return False, ""

def _check_availability(db, alert: Alert, product: Product):
    """Check if product became available/unavailable"""
    target_availability = alert.condition.get("available", True)
    
    latest_price = db.query(PriceHistory).filter(
        PriceHistory.product_id == product.id
    ).order_by(desc(PriceHistory.checked_at)).first()
    
    if not latest_price:
        return False, ""
    
    if latest_price.availability == target_availability:
        status = "available" if target_availability else "unavailable"
        return True, f"Product is now {status}"
    
    return False, ""

def _check_competitor_price(db, alert: Alert, product: Product):
    """Check if competitor price is lower than base price"""
    margin = alert.condition.get("margin", 0)
    
    if not product.base_price:
        return False, ""
    
    # Get all latest prices
    latest_prices = db.query(PriceHistory, Source.name).join(Source).filter(
        PriceHistory.product_id == product.id
    ).order_by(desc(PriceHistory.checked_at)).limit(10).all()
    
    for price_history, source_name in latest_prices:
        if price_history.price < (product.base_price - margin):
            return True, f"{source_name} has lower price: {price_history.price} PLN (your price: {product.base_price} PLN)"
    
    return False, ""

@celery_app.task(name='app.tasks.alert_tasks.check_all_alerts')
def check_all_alerts():
    """Check all active alerts"""
    db = SessionLocal()
    
    try:
        alerts = db.query(Alert).filter(Alert.is_active == True).all()
        
        logger.info(f"Checking {len(alerts)} alerts")
        
        tasks = []
        for alert in alerts:
            task = check_alert.delay(alert.id)
            tasks.append(task)
        
        return {"status": "queued", "alerts_checked": len(tasks)}
        
    except Exception as e:
        logger.error(f"Error in check_all_alerts: {e}")
        return {"status": "error", "error": str(e)}
    finally:
        db.close()
