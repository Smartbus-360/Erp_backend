from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

from app.database import get_db
from app.auth import get_current_user
from app.models.student import Student
from app.models.employee import Employee
from app.models.institute import Institute
from app.models.student_attendance import StudentAttendance
from app.models.employee_attendance import EmployeeAttendance
from app.models.fee_payment import FeePayment

router = APIRouter(prefix="/dashboard1", tags=["Dashboard"])


@router.get("/summary")
def dashboard_summary(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    institute_id = user.institute_id
    today = date.today()
    month_start = today.replace(day=1)

    # ================= STUDENTS =================
    total_students = db.query(Student).filter(
        Student.institute_id == institute_id
    ).count()

    students_this_month = db.query(Student).filter(
        Student.institute_id == institute_id,
        Student.admission_date >= month_start
    ).count()

    # ================= EMPLOYEES =================
    total_employees = db.query(Employee).filter(
        Employee.institute_id == institute_id
    ).count()

    # ================= STUDENT ATTENDANCE =================
    present_students = db.query(StudentAttendance).filter(
        StudentAttendance.institute_id == institute_id,
        StudentAttendance.date == today,      # ✅ FIXED
        StudentAttendance.status == "present"
    ).count()

    # ================= EMPLOYEE ATTENDANCE =================
    present_employees = db.query(EmployeeAttendance).filter(
        EmployeeAttendance.institute_id == institute_id,
        EmployeeAttendance.date == today,     # ✅ FIXED
        EmployeeAttendance.status == "present"
    ).count()

    students_percent = (
        int((present_students / total_students) * 100)
        if total_students else 0
    )

    employees_percent = (
        int((present_employees / total_employees) * 100)
        if total_employees else 0
    )

    # ================= FEES =================
    month_collected = db.query(func.sum(FeePayment.amount)).filter(
        FeePayment.institute_id == institute_id,
        FeePayment.payment_date >= month_start   # ✅ REAL FIELD
    ).scalar() or 0

    # ================= INSTITUTE =================
    institute = db.query(Institute).filter(
        Institute.id == institute_id
    ).first()

    return {
        "students": {
            "total": total_students,
            "this_month": students_this_month
        },
        "employees": {
            "total": total_employees,
            "this_month": total_employees
        },
        "attendance": {
            "students_today_percent": students_percent,
            "employees_today_percent": employees_percent
        },
        "fees": {
            "month_collected": month_collected,
            "month_pending": 0
        },
        "institute": {
            "name": institute.name if institute else "",
            "verified": False
        }
    }
