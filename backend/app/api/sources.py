from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.database import get_db
from app.models.models import Source as SourceModel, ProductSource as ProductSourceModel
from app.schemas.schemas import Source, SourceCreate, SourceUpdate, ProductSource, ProductSourceCreate
from app.api.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[Source])
def get_sources(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(SourceModel)
    
    if is_active is not None:
        query = query.filter(SourceModel.is_active == is_active)
    
    return query.offset(skip).limit(limit).all()

@router.get("/{source_id}", response_model=Source)
def get_source(source_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    source = db.query(SourceModel).filter(SourceModel.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return source

@router.post("/", response_model=Source)
def create_source(source: SourceCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Check if source name already exists
    existing = db.query(SourceModel).filter(SourceModel.name == source.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Source with this name already exists")
    
    db_source = SourceModel(**source.model_dump())
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source

@router.put("/{source_id}", response_model=Source)
def update_source(source_id: int, source: SourceUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_source = db.query(SourceModel).filter(SourceModel.id == source_id).first()
    if not db_source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    update_data = source.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_source, field, value)
    
    db.commit()
    db.refresh(db_source)
    return db_source

@router.delete("/{source_id}")
def delete_source(source_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_source = db.query(SourceModel).filter(SourceModel.id == source_id).first()
    if not db_source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    db.delete(db_source)
    db.commit()
    return {"message": "Source deleted successfully"}

# Product-Source Mappings
@router.get("/product-sources/", response_model=List[ProductSource])
def get_product_sources(
    product_id: Optional[int] = None,
    source_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(ProductSourceModel)
    
    if product_id:
        query = query.filter(ProductSourceModel.product_id == product_id)
    if source_id:
        query = query.filter(ProductSourceModel.source_id == source_id)
    
    return query.all()

@router.post("/product-sources/", response_model=ProductSource)
def create_product_source(
    product_source: ProductSourceCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_product_source = ProductSourceModel(**product_source.model_dump())
    db.add(db_product_source)
    db.commit()
    db.refresh(db_product_source)
    return db_product_source

@router.delete("/product-sources/{product_source_id}")
def delete_product_source(
    product_source_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_ps = db.query(ProductSourceModel).filter(ProductSourceModel.id == product_source_id).first()
    if not db_ps:
        raise HTTPException(status_code=404, detail="Product-Source mapping not found")
    
    db.delete(db_ps)
    db.commit()
    return {"message": "Product-Source mapping deleted successfully"}
