from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy.exc import ProgrammingError

from app.models.database import get_db
from app.models.models import Alert as AlertModel
from app.schemas.schemas import Alert, AlertCreate, AlertUpdate
from app.api.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[Alert])
def get_alerts(
    skip: int = 0,
    limit: int = 100,
    is_active: bool = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        query = db.query(AlertModel).filter(AlertModel.user_id == current_user.id)

        if is_active is not None:
            query = query.filter(AlertModel.is_active == is_active)

        return query.offset(skip).limit(limit).all()
    except ProgrammingError as e:
        msg = str(e.orig) if getattr(e, "orig", None) else str(e)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "database_schema_mismatch",
                "message": "Błąd schematu bazy danych. Uruchom migracje Alembic.",
                "db_error": msg,
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "alerts_list_failed",
                "message": "Nie udało się pobrać alertów.",
                "details": str(e),
            },
        )

@router.get("/{alert_id}", response_model=Alert)
def get_alert(alert_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    alert = db.query(AlertModel).filter(
        AlertModel.id == alert_id,
        AlertModel.user_id == current_user.id
    ).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@router.post("/", response_model=Alert)
def create_alert(alert: AlertCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_alert = AlertModel(**alert.model_dump(), user_id=current_user.id)
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

@router.put("/{alert_id}", response_model=Alert)
def update_alert(
    alert_id: int,
    alert: AlertUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_alert = db.query(AlertModel).filter(
        AlertModel.id == alert_id,
        AlertModel.user_id == current_user.id
    ).first()
    if not db_alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    update_data = alert.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_alert, field, value)
    
    db.commit()
    db.refresh(db_alert)
    return db_alert

@router.delete("/{alert_id}")
def delete_alert(alert_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_alert = db.query(AlertModel).filter(
        AlertModel.id == alert_id,
        AlertModel.user_id == current_user.id
    ).first()
    if not db_alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    db.delete(db_alert)
    db.commit()
    return {"message": "Alert deleted successfully"}
