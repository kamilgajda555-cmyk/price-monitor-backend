from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, JSON
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
    brand = Column(String)
    description = Column(Text)
    base_price = Column(Float)  # Your reference price
    image_url = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    price_history = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")
    product_sources = relationship("ProductSource", back_populates="product", cascade="all, delete-orphan")

class Source(Base):
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    type = Column(String)  # marketplace, distributor
    base_url = Column(String)
    is_active = Column(Boolean, default=True)
    scraper_config = Column(JSON)  # CSS selectors, API endpoints, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    
    product_sources = relationship("ProductSource", back_populates="source")

class ProductSource(Base):
    __tablename__ = "product_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    source_url = Column(String, nullable=False)
    source_product_id = Column(String)  # ID in source system
    selector_config = Column(JSON)  # Custom selectors for this product
    is_active = Column(Boolean, default=True)
    last_checked = Column(DateTime)
    last_price = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    product = relationship("Product", back_populates="product_sources")
    source = relationship("Source", back_populates="product_sources")

class PriceHistory(Base):
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String, default="PLN")
    availability = Column(Boolean, default=True)
    checked_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    product = relationship("Product", back_populates="price_history")

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"))
    alert_type = Column(String)  # price_drop, price_increase, availability, competitor
    condition = Column(JSON)  # threshold, percentage, etc.
    is_active = Column(Boolean, default=True)
    last_triggered = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="alerts")

class ScrapeJob(Base):
    __tablename__ = "scrape_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    source_id = Column(Integer, ForeignKey("sources.id"))
    status = Column(String)  # pending, running, completed, failed
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    prices_found = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
