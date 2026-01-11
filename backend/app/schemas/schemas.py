from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# Product Schemas
class ProductBase(BaseModel):
    name: str
    sku: Optional[str] = None
    ean: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    description: Optional[str] = None
    base_price: Optional[float] = None
    image_url: Optional[str] = None
    is_active: bool = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    ean: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    description: Optional[str] = None
    base_price: Optional[float] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None

class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProductWithPrices(Product):
    current_prices: List[Dict[str, Any]] = []
    price_trend: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    avg_price: Optional[float] = None

# Source Schemas
class SourceBase(BaseModel):
    name: str
    type: Optional[str] = None
    base_url: Optional[str] = None
    is_active: bool = True
    scraper_config: Optional[Dict[str, Any]] = None

class SourceCreate(SourceBase):
    pass

class SourceUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    base_url: Optional[str] = None
    is_active: Optional[bool] = None
    scraper_config: Optional[Dict[str, Any]] = None

class Source(SourceBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# ProductSource Schemas
class ProductSourceBase(BaseModel):
    product_id: int
    source_id: int
    source_url: str
    source_product_id: Optional[str] = None
    selector_config: Optional[Dict[str, Any]] = None
    is_active: bool = True

class ProductSourceCreate(ProductSourceBase):
    pass

class ProductSource(ProductSourceBase):
    id: int
    last_checked: Optional[datetime] = None
    last_price: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# PriceHistory Schemas
class PriceHistoryBase(BaseModel):
    product_id: int
    source_id: int
    price: float
    currency: str = "PLN"
    availability: bool = True

class PriceHistoryCreate(PriceHistoryBase):
    pass

class PriceHistory(PriceHistoryBase):
    id: int
    checked_at: datetime
    
    class Config:
        from_attributes = True

# Alert Schemas
class AlertBase(BaseModel):
    product_id: Optional[int] = None
    alert_type: str
    condition: Dict[str, Any]
    is_active: bool = True

class AlertCreate(AlertBase):
    pass

class AlertUpdate(BaseModel):
    alert_type: Optional[str] = None
    condition: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class Alert(AlertBase):
    id: int
    user_id: int
    last_triggered: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Dashboard Schemas
class DashboardStats(BaseModel):
    total_products: int
    active_products: int
    total_sources: int
    active_sources: int
    total_price_checks_today: int
    products_with_price_drop: int
    products_with_price_increase: int
    average_price_change: float

class PriceAlert(BaseModel):
    product_id: int
    product_name: str
    source_name: str
    old_price: float
    new_price: float
    change_percent: float
    checked_at: datetime

# Report Schemas
class ReportRequest(BaseModel):
    report_type: str  # products, price_changes, sources
    format: str  # csv, excel, pdf
    filters: Optional[Dict[str, Any]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None

class BulkProductImport(BaseModel):
    products: List[ProductCreate]
