from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.models.employee import Employee
from app.models.employee_permission import EmployeePermission
from app.schemas.employee import EmployeeCreate, EmployeeResponse, PermissionUpdate,EmployeeCreateResponse,EmployeeListResponse
from app.dependencies import admin_or_superadmin
from app.models.user import User
from app.security import hash_password
from app.schemas.employee_login import EmployeeLoginCreate

router = APIRouter(prefix="/employees", tags=["Employees"])

@router.post("/", response_model=EmployeeCreateResponse)
def add_employee(
    data: EmployeeCreate,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    employee = Employee(
    name=data.name,
    designation=data.designation,
    phone=data.phone,
    gender=data.gender,
    education=data.education,
    religion=data.religion,
    address=data.address,
    institute_id=user.institute_id
)


    db.add(employee)
    db.commit()
    db.refresh(employee)

    perms = EmployeePermission(employee_id=employee.id)
    db.add(perms)
    db.commit()

    return employee

# @router.get("/", response_model=list[EmployeeResponse])
# def list_employees(
#     db: Session = Depends(get_db),
#     user=Depends(admin_or_superadmin)
# ):
#     if user.role == "superadmin":
#         return db.query(Employee).all()

#     return db.query(Employee).filter(
#         Employee.institute_id == user.institute_id
#     ).all()

@router.get("/", response_model=list[EmployeeListResponse])
def list_employees(
    search: str | None = None,
    role: str | None = None,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    q = db.query(Employee).filter(
        Employee.institute_id == user.institute_id
    )

    if search:
        q = q.filter(Employee.name.ilike(f"%{search}%"))
    
    if role:
        q = q.filter(Employee.designation.ilike(f"%{role}%"))

    employees = q.all()

    result = []
    for emp in employees:
        result.append({
            "id": emp.id,
            "name": emp.name,
            "designation": emp.designation,
            "phone": emp.phone,
            "has_login": emp.user_id is not None,
            "login_email": emp.user.email if emp.user else None,
            "is_active": emp.user.is_active if emp.user else False
        })

    return result


@router.put("/{employee_id}/permissions")
def update_permissions(
    employee_id: int,
    data: PermissionUpdate,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    employee = db.query(Employee).filter(
        Employee.id == employee_id,
        Employee.institute_id == user.institute_id
    ).first()

    if not employee:
        raise HTTPException(status_code=404)

    perms = db.query(EmployeePermission).filter(
        EmployeePermission.employee_id == employee.id
    ).first()

    for field, value in data.dict().items():
        setattr(perms, field, value)

    db.commit()
    return {"message": "Permissions updated"}

def attendance_access(user=Depends(get_current_user), db=Depends(get_db)):
    if user.role == "admin":
        return user

    if user.role == "employee":
        perms = db.query(EmployeePermission).filter(
            EmployeePermission.employee_id == user.employee.id
        ).first()

        if not perms.can_attendance:
            raise HTTPException(status_code=403)

        return user

    raise HTTPException(status_code=403)

@router.post("/{employee_id}/create-login")
def create_employee_login(
    employee_id: int,
    data: EmployeeLoginCreate,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    employee = db.query(Employee).filter(
        Employee.id == employee_id,
        Employee.institute_id == user.institute_id
    ).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    new_user = User(
        name=employee.name,
        email=data.email,
        password=hash_password(data.password),
        role="employee",
        institute_id=user.institute_id
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    employee.user_id = new_user.id
    db.commit()

    return {
        "message": "Employee login created successfully",
        "email": new_user.email
    }

@router.put("/{employee_id}/toggle-login")
def toggle_employee_login(
    employee_id: int,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    employee = db.query(Employee).filter(
        Employee.id == employee_id,
        Employee.institute_id == user.institute_id
    ).first()

    if not employee or not employee.user:
        raise HTTPException(404, "Login not found")

    employee.user.is_active = not employee.user.is_active
    db.commit()

    return {
        "message": "Login status updated",
        "is_active": employee.user.is_active
    }

@router.put("/{employee_id}/change-password")
def change_employee_password(
    employee_id: int,
    data: EmployeeLoginCreate,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    employee = db.query(Employee).filter(
        Employee.id == employee_id,
        Employee.institute_id == user.institute_id
    ).first()

    if not employee or not employee.user:
        raise HTTPException(404, "Login not found")

    employee.user.password = hash_password(data.password)
    db.commit()

    return {"message": "Password updated"}
@router.get("/{employee_id}/permissions", dependencies=[Depends(admin_or_superadmin)])
def get_employee_permissions(
    employee_id: int,
    db: Session = Depends(get_db)
):
    perm = db.query(EmployeePermission).filter(
        EmployeePermission.employee_id == employee_id
    ).first()

    if not perm:
        return {
            "can_students": False,
            "can_attendance": False,
            "can_exams": False,
            "can_homework": False
        }

    return perm

@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    employee = db.query(Employee).filter(
        Employee.id == employee_id,
        Employee.institute_id == user.institute_id
    ).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    return {
        "id": employee.id,
        "name": employee.name,
        "designation": employee.designation,
        "phone": employee.phone,
    }

@router.get("/{employee_id}")
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    return {
        "id": emp.id,
        "name": emp.name,
        "email": emp.email,
        "mobile": emp.mobile,
        "role": emp.role,
        "designation": emp.designation,
        "salary": emp.salary,
        "joining_date": emp.joining_date
    }
