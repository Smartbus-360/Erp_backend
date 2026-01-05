from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.employee_salary import EmployeeSalary
from app.models.salary_payment import SalaryPayment
from app.models.employee import Employee
from app.dependencies import admin_or_superadmin
from app.auth import get_current_user
from app.schemas.salary_schema import SetSalary, PaySalary

router = APIRouter(prefix="/salary", tags=["Salary"])

@router.post("/set")
def set_salary(
    data: SetSalary,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    emp = db.query(Employee).filter(
        Employee.id == data.employee_id,
        Employee.institute_id == user.institute_id
    ).first()

    if not emp:
        raise HTTPException(status_code=404)

    record = db.query(EmployeeSalary).filter(
        EmployeeSalary.employee_id == data.employee_id
    ).first()

    if record:
        record.monthly_salary = data.monthly_salary
    else:
        record = EmployeeSalary(
            **data.dict(),
            institute_id=user.institute_id
        )
        db.add(record)

    db.commit()
    return {"message": "Salary set"}

@router.post("/pay")
def pay_salary(
    data: PaySalary,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    exists = db.query(SalaryPayment).filter(
        SalaryPayment.employee_id == data.employee_id,
        SalaryPayment.month == data.month,
        SalaryPayment.institute_id == user.institute_id
    ).first()

    if exists:
        raise HTTPException(
            status_code=400,
            detail="Salary already paid for this month"
        )
    payment = SalaryPayment(
        **data.dict(),
        institute_id=user.institute_id
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return {"message": "Salary paid",
            "payment_id": payment.id}

@router.get("/history/{employee_id}")
def salary_history(
    employee_id: int,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    return db.query(SalaryPayment).filter(
        SalaryPayment.employee_id == employee_id,
        SalaryPayment.institute_id == user.institute_id
    ).all()

@router.get("/me")
def my_salary(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role != "employee":
        raise HTTPException(status_code=403)

    return db.query(SalaryPayment).filter(
    SalaryPayment.employee_id == user.employee_id,
    SalaryPayment.institute_id == user.institute_id
).all()


@router.get("/slip/{payment_id}")
def salary_slip(
    payment_id: int,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    pay = db.query(SalaryPayment).join(Employee).filter(
        SalaryPayment.id == payment_id,
        SalaryPayment.institute_id == user.institute_id
    ).first()

    if not pay:
        raise HTTPException(status_code=404)

    return {
        "employee": pay.employee.name,
        "designation": pay.employee.designation,
        "month": pay.month,
        "paid_on": pay.paid_on,
        "amount": pay.amount,
        "bonus": pay.bonus,
        "deduction": pay.deduction,
        "net_amount": pay.amount + pay.bonus - pay.deduction
    }
