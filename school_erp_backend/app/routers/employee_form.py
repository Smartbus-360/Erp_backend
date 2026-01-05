from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.employee_form_field import EmployeeFormField
from app.models.employee_extra_data import EmployeeExtraData
from app.schemas.employee_form_schema import (
    EmployeeFormFieldCreate,
    EmployeeFormFieldResponse,
    EmployeeExtraDataCreate
)
from app.dependencies import admin_or_superadmin

router = APIRouter(prefix="/employees/form", tags=["Employee Form"])

@router.post("/fields", response_model=EmployeeFormFieldResponse)
def add_employee_form_field(
    data: EmployeeFormFieldCreate,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    exists = db.query(EmployeeFormField).filter(
        EmployeeFormField.institute_id == user.institute_id,
        EmployeeFormField.field_key == data.field_key
    ).first()

    if exists:
        raise HTTPException(400, "Field key already exists")

    field = EmployeeFormField(
        **data.dict(),
        institute_id=user.institute_id
    )
    db.add(field)
    db.commit()
    db.refresh(field)
    return field

@router.get("/fields", response_model=list[EmployeeFormFieldResponse])
def get_employee_form_fields(
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    return db.query(EmployeeFormField).filter(
        EmployeeFormField.institute_id == user.institute_id,
        EmployeeFormField.is_active == True
    ).all()

@router.post("/extra-data")
def save_employee_extra_data(
    data: EmployeeExtraDataCreate,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    for key, value in data.values.items():
        db.add(EmployeeExtraData(
            employee_id=data.employee_id,
            field_key=key,
            value=str(value)
        ))

    db.commit()
    return {"message": "Employee extra data saved"}
