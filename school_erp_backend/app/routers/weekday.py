from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.weekday import Weekday
from app.dependencies import admin_or_superadmin
from app.schemas.weekday_schema import WeekdayCreate

router = APIRouter(
    prefix="/weekdays",
    tags=["Weekdays"]
)

@router.post("/")
def add_weekday(
    data: WeekdayCreate,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    weekday = Weekday(
        name=data.name,
        institute_id=user.institute_id
    )
    db.add(weekday)
    db.commit()
    db.refresh(weekday)

    return weekday

@router.get("/")
def get_weekdays(
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    return (
        db.query(Weekday)
        .filter(Weekday.institute_id == user.institute_id)
        .order_by(Weekday.id)
        .all()
    )
