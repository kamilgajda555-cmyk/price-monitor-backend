from app.tasks.celery_app import celery_app
from app.models.database import SessionLocal
from app.models.models import Product, ProductSource, Source, PriceHistory, ScrapeJob
from app.scrapers.universal_scraper import get_scraper
from datetime import datetime
import logging
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@celery_app.task(name='app.tasks.scraping_tasks.scrape_product')
def scrape_product(product_id: int, source_id: int):
    """Scrape price for a single product from a specific source"""
    db = SessionLocal()
    
    try:
        # Get product source mapping
        product_source = db.query(ProductSource).filter(
            ProductSource.product_id == product_id,
            ProductSource.source_id == source_id,
            ProductSource.is_active == True
        ).first()
        
        if not product_source:
            logger.warning(f"No active product-source mapping for product {product_id}, source {source_id}")
            return {"status": "skipped", "reason": "No active mapping"}
        
        # Get source info
        source = db.query(Source).filter(Source.id == source_id).first()
        if not source or not source.is_active:
            logger.warning(f"Source {source_id} not found or inactive")
            return {"status": "skipped", "reason": "Source inactive"}
        
        # Get scraper
        scraper = get_scraper(source.name)
        
        # Prepare config
        config = product_source.selector_config or source.scraper_config or {}
        
        # Scrape price (run async function in sync context)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(scraper.scrape_price(product_source.source_url, config))
        loop.close()
        
        if "error" in result:
            logger.error(f"Error scraping product {product_id} from source {source_id}: {result['error']}")
            return {"status": "error", "error": result["error"]}
        
        # Save price history
        price_history = PriceHistory(
            product_id=product_id,
            source_id=source_id,
            price=result["price"],
            currency=result.get("currency", "PLN"),
            availability=result.get("availability", True),
            checked_at=datetime.utcnow()
        )
        db.add(price_history)
        
        # Update product source
        product_source.last_checked = datetime.utcnow()
        product_source.last_price = result["price"]
        
        db.commit()
        
        logger.info(f"Successfully scraped product {product_id} from source {source_id}: {result['price']}")
        return {"status": "success", "price": result["price"], "product_id": product_id, "source_id": source_id}
        
    except Exception as e:
        logger.error(f"Error in scrape_product task: {e}")
        db.rollback()
        return {"status": "error", "error": str(e)}
    finally:
        db.close()

@celery_app.task(name='app.tasks.scraping_tasks.scrape_all_products')
def scrape_all_products():
    """Scrape all active products from all active sources"""
    db = SessionLocal()
    
    try:
        # Create scrape job
        scrape_job = ScrapeJob(
            status="running",
            started_at=datetime.utcnow(),
            prices_found=0
        )
        db.add(scrape_job)
        db.commit()
        
        # Get all active product-source mappings
        product_sources = db.query(ProductSource).filter(
            ProductSource.is_active == True
        ).all()
        
        logger.info(f"Starting scraping job for {len(product_sources)} product-source mappings")
        
        # Queue individual scraping tasks
        tasks = []
        for ps in product_sources:
            task = scrape_product.delay(ps.product_id, ps.source_id)
            tasks.append(task)
        
        # Wait for all tasks and count successes
        successful = 0
        failed = 0
        
        for task in tasks:
            try:
                result = task.get(timeout=300)  # 5 minutes timeout
                if result.get("status") == "success":
                    successful += 1
                else:
                    failed += 1
            except Exception as e:
                logger.error(f"Task failed: {e}")
                failed += 1
        
        # Update scrape job
        scrape_job.status = "completed"
        scrape_job.completed_at = datetime.utcnow()
        scrape_job.prices_found = successful
        if failed > 0:
            scrape_job.error_message = f"{failed} tasks failed"
        
        db.commit()
        
        logger.info(f"Scraping job completed: {successful} successful, {failed} failed")
        return {
            "status": "completed",
            "successful": successful,
            "failed": failed,
            "total": len(product_sources)
        }
        
    except Exception as e:
        logger.error(f"Error in scrape_all_products task: {e}")
        if scrape_job:
            scrape_job.status = "failed"
            scrape_job.completed_at = datetime.utcnow()
            scrape_job.error_message = str(e)
            db.commit()
        return {"status": "error", "error": str(e)}
    finally:
        db.close()

@celery_app.task(name='app.tasks.scraping_tasks.scrape_products_by_source')
def scrape_products_by_source(source_id: int):
    """Scrape all products for a specific source"""
    db = SessionLocal()
    
    try:
        product_sources = db.query(ProductSource).filter(
            ProductSource.source_id == source_id,
            ProductSource.is_active == True
        ).all()
        
        logger.info(f"Scraping {len(product_sources)} products for source {source_id}")
        
        tasks = []
        for ps in product_sources:
            task = scrape_product.delay(ps.product_id, ps.source_id)
            tasks.append(task)
        
        return {"status": "queued", "tasks": len(tasks)}
        
    except Exception as e:
        logger.error(f"Error in scrape_products_by_source task: {e}")
        return {"status": "error", "error": str(e)}
    finally:
        db.close()
