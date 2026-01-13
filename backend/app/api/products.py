from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta

from app.models.database import get_db
from app.models.models import Product as ProductModel, PriceHistory, ProductSource, Source
from app.schemas.schemas import Product, ProductCreate, ProductUpdate, ProductWithPrices, BulkProductImport
from app.api.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[ProductWithPrices])
def get_products(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(ProductModel)
    
    if search:
        query = query.filter(
            (ProductModel.name.ilike(f"%{search}%")) |
            (ProductModel.sku.ilike(f"%{search}%")) |
            (ProductModel.ean.ilike(f"%{search}%"))
        )
    
    if category:
        query = query.filter(ProductModel.category == category)
    
    if is_active is not None:
        query = query.filter(ProductModel.is_active == is_active)
    
    products = query.offset(skip).limit(limit).all()
    
    # Enrich with current prices (safe mode - handle empty tables)
    result = []
    for product in products:
        try:
            # Get latest prices from each source
            latest_prices = db.query(
                PriceHistory.source_id,
                PriceHistory.price,
                PriceHistory.checked_at,
                Source.name
            ).join(Source, PriceHistory.source_id == Source.id).filter(
                PriceHistory.product_id == product.id
            ).order_by(desc(PriceHistory.checked_at)).all()
            
            # Get unique latest price per source
            seen_sources = set()
            current_prices = []
            for price_record in latest_prices:
                if price_record.source_id not in seen_sources:
                    seen_sources.add(price_record.source_id)
                    current_prices.append({
                        "source_id": price_record.source_id,
                        "source_name": price_record.name,
                        "price": float(price_record.price) if price_record.price else None,
                        "checked_at": price_record.checked_at
                    })
        except Exception as e:
            # If price history query fails, just use empty prices
            current_prices = []
        
        # Calculate price statistics
        prices = [p["price"] for p in current_prices if p["price"] is not None]
        product_dict = {
            **{k: v for k, v in product.__dict__.items() if not k.startswith('_')},
            "current_prices": current_prices,
            "min_price": min(prices) if prices else None,
            "max_price": max(prices) if prices else None,
            "avg_price": sum(prices) / len(prices) if prices else None,
            "price_trend": "stable"  # Could be calculated from history
        }
        result.append(ProductWithPrices(**product_dict))
    
    return result

@router.get("/{product_id}", response_model=ProductWithPrices)
def get_product(product_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get current prices (safe mode)
    try:
        latest_prices = db.query(
            PriceHistory.source_id,
            PriceHistory.price,
            PriceHistory.checked_at,
            Source.name
        ).join(Source, PriceHistory.source_id == Source.id).filter(
            PriceHistory.product_id == product.id
        ).order_by(desc(PriceHistory.checked_at)).all()
        
        seen_sources = set()
        current_prices = []
        for price_record in latest_prices:
            if price_record.source_id not in seen_sources:
                seen_sources.add(price_record.source_id)
                current_prices.append({
                    "source_id": price_record.source_id,
                    "source_name": price_record.name,
                    "price": float(price_record.price) if price_record.price else None,
                    "checked_at": price_record.checked_at
                })
    except Exception as e:
        current_prices = []
    
    prices = [p["price"] for p in current_prices if p["price"] is not None]
    product_dict = {
        **{k: v for k, v in product.__dict__.items() if not k.startswith('_')},
        "current_prices": current_prices,
        "min_price": min(prices) if prices else None,
        "max_price": max(prices) if prices else None,
        "avg_price": sum(prices) / len(prices) if prices else None,
        "price_trend": "stable"
    }
    
    return ProductWithPrices(**product_dict)

@router.post("/", response_model=Product)
def create_product(product: ProductCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Check if SKU already exists
    if product.sku:
        existing = db.query(ProductModel).filter(ProductModel.sku == product.sku).first()
        if existing:
            raise HTTPException(status_code=400, detail="Product with this SKU already exists")
    
    db_product = ProductModel(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.put("/{product_id}", response_model=Product)
def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = product.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    db_product.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(db_product)
    db.commit()
    return {"message": "Product deleted successfully"}

@router.get("/{product_id}/price-history")
def get_price_history(
    product_id: int,
    source_id: Optional[int] = None,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    date_from = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(PriceHistory, Source.name).join(Source).filter(
        PriceHistory.product_id == product_id,
        PriceHistory.checked_at >= date_from
    )
    
    if source_id:
        query = query.filter(PriceHistory.source_id == source_id)
    
    history = query.order_by(PriceHistory.checked_at).all()
    
    return [
        {
            "id": h[0].id,
            "source_id": h[0].source_id,
            "source_name": h[1],
            "price": h[0].price,
            "currency": h[0].currency,
            "availability": h[0].availability,
            "checked_at": h[0].checked_at
        }
        for h in history
    ]

@router.post("/bulk-import")
def bulk_import_products(
    import_data: BulkProductImport,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    created = []
    errors = []
    
    for product_data in import_data.products:
        try:
            # Check if product exists
            if product_data.sku:
                existing = db.query(ProductModel).filter(ProductModel.sku == product_data.sku).first()
                if existing:
                    errors.append({"sku": product_data.sku, "error": "Already exists"})
                    continue
            
            db_product = ProductModel(**product_data.model_dump())
            db.add(db_product)
            db.commit()
            db.refresh(db_product)
            created.append(db_product.id)
        except Exception as e:
            errors.append({"sku": product_data.sku if product_data.sku else "N/A", "error": str(e)})
    
    return {
        "created": len(created),
        "errors": len(errors),
        "created_ids": created,
        "error_details": errors
    }
