from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.student import Student
from app.dependencies import employee_permission_required

router = APIRouter(prefix="/students", tags=["Students"])

@router.get("/search")
def search_students(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    user=Depends(employee_permission_required("can_fees"))
):
    students = db.query(Student).filter(
        Student.institute_id == user.institute_id,
        Student.full_name.ilike(f"%{q}%")
    ).limit(10).all()

    return [
        {
            "id": s.id,
            "name": s.name,
            "registration_no": s.admission_no,
            "class": s.class_name,
            "section": s.section
        }
        for s in students
    ]
