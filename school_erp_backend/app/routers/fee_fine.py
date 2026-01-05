from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.fee_fine_rule import FeeFineRule
from app.schemas.fee_fine_schema import FeeFineCreate
from app.dependencies import admin_or_superadmin

router = APIRouter(prefix="/fee-fine", tags=["Fee Fine"])

@router.post("/")
def set_fee_fine(
    data: FeeFineCreate,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    rule = FeeFineRule(
        **data.dict(),
        institute_id=user.institute_id
    )
    db.add(rule)
    db.commit()
    return {"message": "Fine rule saved"}

@router.get("/")
def get_fee_fine(
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    return db.query(FeeFineRule).filter(
        FeeFineRule.institute_id == user.institute_id
    ).first()
