from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.period import Period
from app.schemas.period_schema import PeriodCreate, PeriodResponse
from app.dependencies import admin_or_superadmin

router = APIRouter(prefix="/periods", tags=["Periods"])

@router.post("/", response_model=PeriodResponse)
def add_period(
    data: PeriodCreate,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    p = Period(
        **data.dict(),
        institute_id=user.institute_id
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

@router.get("/", response_model=list[PeriodResponse])
def list_periods(
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    return db.query(Period).filter(
        Period.institute_id == user.institute_id
    ).order_by(Period.order_no).all()
