from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date

from app.database import get_db
from app.auth import get_current_user
from app.models.student import Student
from app.models.employee import Employee
from app.models.student_attendance import StudentAttendance
from app.models.employee_attendance import EmployeeAttendance
from app.models.student_fee import StudentFee
from app.models.exam import Exam
from app.models.homework import Homework
from app.models.class_model import SchoolClass

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/admin")
def admin_dashboard(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role not in ["admin", "superadmin"]:
        return {"detail": "Forbidden"}

    today = date.today()

    return {
        "students": db.query(Student).filter(
            Student.institute_id == user.institute_id
        ).count(),

        "employees": db.query(Employee).filter(
            Employee.institute_id == user.institute_id
        ).count(),

        "student_attendance_today": db.query(StudentAttendance).filter(
            StudentAttendance.institute_id == user.institute_id,
            StudentAttendance.date == today,
            StudentAttendance.status == "present"
        ).count(),

        "employee_attendance_today": db.query(EmployeeAttendance).filter(
            EmployeeAttendance.institute_id == user.institute_id,
            EmployeeAttendance.date == today,
            EmployeeAttendance.status == "present"
        ).count(),

        "fee_defaulters": db.query(StudentFee).filter(
            StudentFee.institute_id == user.institute_id,
            StudentFee.is_paid == False
        ).count(),

        "exams": db.query(Exam).filter(
            Exam.institute_id == user.institute_id
        ).count(),

        "active_homework": db.query(Homework).filter(
            Homework.institute_id == user.institute_id,
            Homework.due_date >= today
        ).count()
    }


@router.get("/employee")
def employee_dashboard(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role != "employee":
        return {"detail": "Forbidden"}

    today = date.today()

    # 🔹 Get employee profile
    employee = db.query(Employee).filter(
        Employee.user_id == user.id,
        Employee.institute_id == user.institute_id
    ).first()

    if not employee:
        return {"detail": "Employee profile not found"}

    return {
        "today_attendance_marked": db.query(EmployeeAttendance).filter(
            EmployeeAttendance.employee_id == employee.id,
            EmployeeAttendance.date == today
        ).count() > 0,

        "homework_assigned": db.query(Homework).filter(
            Homework.institute_id == user.institute_id
        ).count(),

        "total_exams": db.query(Exam).filter(
            Exam.institute_id == user.institute_id
        ).count()
    }

@router.get("/student")
def student_dashboard(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role != "student":
        return {"detail": "Forbidden"}

    student = db.query(Student).filter(
        Student.user_id == user.id,
        Student.institute_id == user.institute_id
    ).first()

    if not student:
        return {"detail": "Student profile not found"}

    today = date.today()

    cls = db.query(SchoolClass).filter(
        SchoolClass.name == student.class_name,
        SchoolClass.institute_id == user.institute_id
    ).first()

    exam_count = 0
    if cls:
        exam_count = db.query(Exam).filter(
            Exam.class_id == cls.id,
            Exam.institute_id == user.institute_id
        ).count()

    return {
        "attendance_today": db.query(StudentAttendance).filter(
            StudentAttendance.student_id == student.id,
            StudentAttendance.date == today
        ).count() > 0,

        "pending_homework": db.query(Homework).filter(
            Homework.class_id == student.class_name,
            Homework.due_date >= today
        ).count(),

        "fee_status": "PAID" if db.query(StudentFee).filter(
            StudentFee.student_id == student.id,
            StudentFee.is_paid == True
        ).first() else "PENDING",

        "exams": exam_count
    }
