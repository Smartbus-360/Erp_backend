from fastapi import Depends, HTTPException
from app.auth import get_current_user
from app.models.employee import Employee
from app.models.employee_permission import EmployeePermission
from app.database import get_db
from sqlalchemy.orm import Session


def superadmin_only(user=Depends(get_current_user)):
    if user.role != "superadmin":
        raise HTTPException(status_code=403, detail="SuperAdmin only")
    return user

def admin_or_superadmin(user=Depends(get_current_user)):
    if user.role not in ["admin", "superadmin"]:
        raise HTTPException(status_code=403)
    return user

def employee_permission_required(permission: str):
    def checker(
        user=Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        if user.role == "admin":
            return user

        if user.role != "employee":
            raise HTTPException(status_code=403)

        employee = db.query(Employee).filter(
            Employee.user_id == user.id
        ).first()

        if not employee:
            raise HTTPException(status_code=403)

        perms = db.query(EmployeePermission).filter(
            EmployeePermission.employee_id == employee.id
        ).first()

        if not perms or not getattr(perms, permission):
            raise HTTPException(
                status_code=403,
                detail="Permission denied"
            )

        return user

    return checker
