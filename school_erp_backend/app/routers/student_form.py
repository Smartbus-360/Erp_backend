from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.student_form_field import StudentFormField
from app.models.student_extra_data import StudentExtraData
from app.schemas.student_form_schema import (
    StudentFormFieldCreate,
    StudentFormFieldResponse,
    StudentExtraDataCreate
)
from app.dependencies import admin_or_superadmin

router = APIRouter(prefix="/students/form", tags=["Student Admission Form"])

@router.post("/fields", response_model=StudentFormFieldResponse)
def add_form_field(
    data: StudentFormFieldCreate,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    exists = db.query(StudentFormField).filter(
        StudentFormField.institute_id == user.institute_id,
        StudentFormField.field_key == data.field_key
    ).first()

    if exists:
        raise HTTPException(400, "Field key already exists")

    field = StudentFormField(
        **data.dict(),
        institute_id=user.institute_id
    )
    db.add(field)
    db.commit()
    db.refresh(field)
    return field

@router.get("/fields", response_model=list[StudentFormFieldResponse])
def get_form_fields(
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    return db.query(StudentFormField).filter(
        StudentFormField.institute_id == user.institute_id,
        StudentFormField.is_active == True
    ).all()

@router.post("/extra-data")
def save_student_extra_data(
    data: StudentExtraDataCreate,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    for key, value in data.values.items():
        db.add(StudentExtraData(
            student_id=data.student_id,
            field_key=key,
            value=str(value)
        ))

    db.commit()
    return {"message": "Extra data saved"}
