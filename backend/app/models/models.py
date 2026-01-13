from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, JSON, Index, Date, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    alerts = relationship("Alert", back_populates="user")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    sku = Column(String, unique=True, index=True)
    ean = Column(String, index=True)
    category = Column(String, index=True)
    brand = Column(String, index=True)
    description = Column(Text)
    base_price = Column(Float)  # Your reference price
    image_url = Column(String)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Note: Removed cached stats (min_price, max_price, avg_price, last_scraped)
    # These will be calculated on-the-fly from price_history when needed
    
    price_history = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")
    product_sources = relationship("ProductSource", back_populates="product", cascade="all, delete-orphan")
    daily_stats = relationship("DailyPriceStats", back_populates="product", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_product_active_category', 'is_active', 'category'),
        Index('idx_product_brand_active', 'brand', 'is_active'),
    )

class Source(Base):
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    type = Column(String, index=True)  # marketplace, distributor
    base_url = Column(String)
    is_active = Column(Boolean, default=True, index=True)
    scraper_config = Column(JSON)  # CSS selectors, API endpoints, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Note: Removed scraping metadata (last_scrape_*, total_products)
    # These will be tracked in scrape_jobs table instead
    
    product_sources = relationship("ProductSource", back_populates="source")

class ProductSource(Base):
    __tablename__ = "product_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    source_id = Column(Integer, ForeignKey("sources.id", ondelete="CASCADE"), nullable=False)
    source_url = Column(String, nullable=False)
    source_product_id = Column(String, index=True)  # ID in source system
    selector_config = Column(JSON)  # Custom selectors for this product
    is_active = Column(Boolean, default=True, index=True)
    
    # Current state
    last_checked = Column(DateTime, index=True)
    last_price = Column(Float)
    # Note: last_availability removed (not in DB schema)
    
    # Note: Removed price_change cache columns
    # These will be calculated from price_history when needed
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    product = relationship("Product", back_populates="product_sources")
    source = relationship("Source", back_populates="product_sources")
    
    __table_args__ = (
        Index('idx_product_source_active', 'product_id', 'source_id', 'is_active'),
        Index('idx_source_product_active', 'source_id', 'product_id', 'is_active'),
        Index('idx_product_source_last_checked', 'product_id', 'last_checked'),
    )

class PriceHistory(Base):
    """
    Raw price history - partitioned by date for performance.
    For large scale (10k products × 20 sources × 365 days = 73M records/year),
    use PostgreSQL table partitioning by month.
    """
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    source_id = Column(Integer, ForeignKey("sources.id", ondelete="CASCADE"), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)  # Use Numeric for exact prices
    currency = Column(String, default="PLN")
    availability = Column(Boolean, default=True)
    checked_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Additional metadata
    shipping_cost = Column(Numeric(10, 2))
    discount_percentage = Column(Float)
    stock_quantity = Column(Integer)  # If available
    
    product = relationship("Product", back_populates="price_history")
    
    __table_args__ = (
        # Composite indexes for common queries
        Index('idx_price_product_date', 'product_id', 'checked_at'),
        Index('idx_price_source_date', 'source_id', 'checked_at'),
        Index('idx_price_product_source_date', 'product_id', 'source_id', 'checked_at'),
        Index('idx_price_date', 'checked_at'),  # For partitioning
    )

class DailyPriceStats(Base):
    """
    Aggregated daily statistics per product.
    Pre-calculated for fast dashboard/histogram queries.
    Only 10k products × 365 days = 3.65M records/year (much smaller!)
    """
    __tablename__ = "daily_price_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    
    # Aggregated prices across all sources
    min_price = Column(Numeric(10, 2))
    max_price = Column(Numeric(10, 2))
    avg_price = Column(Numeric(10, 2))
    median_price = Column(Numeric(10, 2))
    
    # Price changes
    change_from_previous = Column(Numeric(10, 2))  # Absolute change
    change_percentage = Column(Float)  # Percentage change
    
    # Availability
    sources_available = Column(Integer)  # Number of sources with stock
    total_sources_checked = Column(Integer)
    
    # Best offer
    best_source_id = Column(Integer, ForeignKey("sources.id"))
    best_price = Column(Numeric(10, 2))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    product = relationship("Product", back_populates="daily_stats")
    
    __table_args__ = (
        Index('idx_daily_stats_product_date', 'product_id', 'date'),
        Index('idx_daily_stats_date', 'date'),
        # Unique constraint to prevent duplicate daily records
        Index('idx_daily_stats_unique', 'product_id', 'date', unique=True),
    )

class SourceDailyStats(Base):
    """
    Aggregated daily statistics per source.
    For monitoring source health and performance.
    """
    __tablename__ = "source_daily_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    
    # Scraping stats
    products_scraped = Column(Integer, default=0)
    successful_scrapes = Column(Integer, default=0)
    failed_scrapes = Column(Integer, default=0)
    avg_response_time = Column(Float)  # In seconds
    
    # Price stats
    avg_price_change = Column(Float)  # Average price change across products
    products_price_increased = Column(Integer, default=0)
    products_price_decreased = Column(Integer, default=0)
    products_unavailable = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_source_daily_stats_source_date', 'source_id', 'date'),
        Index('idx_source_daily_stats_unique', 'source_id', 'date', unique=True),
    )

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    alert_type = Column(String, index=True)  # price_drop, price_increase, availability, competitor
    condition = Column(JSON)  # threshold, percentage, etc.
    is_active = Column(Boolean, default=True, index=True)
    last_triggered = Column(DateTime)
    trigger_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="alerts")
    
    __table_args__ = (
        Index('idx_alert_user_active', 'user_id', 'is_active'),
        Index('idx_alert_product_active', 'product_id', 'is_active'),
    )

class ScrapeJob(Base):
    __tablename__ = "scrape_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"))
    source_id = Column(Integer, ForeignKey("sources.id", ondelete="SET NULL"))
    
    # Job metadata
    job_type = Column(String, index=True)  # full, product, source, batch
    status = Column(String, index=True)  # queued, running, completed, failed
    celery_task_id = Column(String, index=True)
    
    # Timing
    started_at = Column(DateTime, index=True)
    completed_at = Column(DateTime)
    duration_seconds = Column(Float)
    
    # Results
    products_processed = Column(Integer, default=0)
    prices_found = Column(Integer, default=0)
    prices_updated = Column(Integer, default=0)
    errors_count = Column(Integer, default=0)
    error_message = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_scrape_job_status_date', 'status', 'started_at'),
        Index('idx_scrape_job_type_date', 'job_type', 'started_at'),
    )
