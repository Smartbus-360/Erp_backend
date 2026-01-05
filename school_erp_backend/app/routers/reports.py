from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date

from app.database import get_db
from app.auth import get_current_user
from app.models.student_attendance import StudentAttendance
from app.models.employee_attendance import EmployeeAttendance
from app.models.exam_mark import ExamMark
from app.models.exam import Exam
from app.models.student import Student
from app.models.subject import Subject
from app.models.student_fee import StudentFee
from app.models.fee_payment import FeePayment
from app.models.salary_payment import SalaryPayment

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/attendance/students")
def student_attendance_report(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return db.query(
        Student.name,
        StudentAttendance.date,
        StudentAttendance.status
    ).join(
        Student, Student.id == StudentAttendance.student_id
    ).filter(
        StudentAttendance.institute_id == user.institute_id,
        StudentAttendance.date.between(start_date, end_date)
    ).all()

@router.get("/attendance/employees")
def employee_attendance_report(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return db.query(
        EmployeeAttendance.employee_id,
        EmployeeAttendance.date,
        EmployeeAttendance.status
    ).filter(
        EmployeeAttendance.institute_id == user.institute_id,
        EmployeeAttendance.date.between(start_date, end_date)
    ).all()

@router.get("/results/class")
def exam_result_report(
    exam_id: int,
    class_name: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return db.query(
        Student.name,
        Subject.name.label("subject"),
        ExamMark.marks
    ).join(
        Student, Student.id == ExamMark.student_id
    ).join(
        Subject, Subject.id == ExamMark.subject_id
    ).filter(
        ExamMark.exam_id == exam_id,
        Student.class_name == class_name,
        Student.institute_id == user.institute_id
    ).all()

@router.get("/fees/collection")
def fee_collection_report(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return db.query(FeePayment).filter(
        FeePayment.institute_id == user.institute_id,
        FeePayment.payment_date.between(start_date, end_date)
    ).all()

@router.get("/fees/defaulters")
def fee_defaulters_report(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return db.query(StudentFee).filter(
        StudentFee.institute_id == user.institute_id,
        StudentFee.is_paid == False
    ).all()

@router.get("/salary")
def salary_report(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return db.query(SalaryPayment).filter(
        SalaryPayment.institute_id == user.institute_id,
        SalaryPayment.payment_date.between(start_date, end_date)
    ).all()
