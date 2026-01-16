from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.employee_role import EmployeeRole
from app.dependencies import admin_or_superadmin

router = APIRouter(prefix="/employee-roles", tags=["Employee Roles"])

@router.post("/")
def create_role(data: dict, db: Session = Depends(get_db),
                user=Depends(admin_or_superadmin)):
    role = EmployeeRole(
        name=data["name"],
        slug=data["name"].lower().replace(" ", "_"),
        institute_id=user.institute_id
    )
    db.add(role)
    db.commit()
    return role

@router.get("/")
def list_roles(db: Session = Depends(get_db),
               user=Depends(admin_or_superadmin)):
    return db.query(EmployeeRole).filter(
        EmployeeRole.institute_id == user.institute_id,
        EmployeeRole.is_active == True
    ).all()
