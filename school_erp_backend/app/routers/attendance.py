from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.attendance import (
    StudentAttendanceCreate,
    EmployeeAttendanceCreate
)
from app.models.student_attendance import StudentAttendance
from app.models.employee_attendance import EmployeeAttendance
from app.models.student import Student
from app.models.employee import Employee
from app.dependencies import admin_or_superadmin
from app.dependencies import employee_permission_required

router = APIRouter(prefix="/attendance", tags=["Attendance"])

@router.post("/students")
def mark_student_attendance(
    data: StudentAttendanceCreate,
    db: Session = Depends(get_db),
    user=Depends(employee_permission_required("can_attendance"))
):
    student = db.query(Student).filter(
        Student.id == data.student_id,
        Student.institute_id == user.institute_id,
        StudentAttendance.institute_id == user.institute_id
    ).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    record = db.query(StudentAttendance).filter(
        StudentAttendance.student_id == data.student_id,
        StudentAttendance.date == data.date
    ).first()

    if record:
        record.status = data.status
    else:
        record = StudentAttendance(
            student_id=data.student_id,
            class_id=data.class_id,
            section_id=data.section_id,
            institute_id=user.institute_id,
            date=data.date,
            status=data.status
        )
        db.add(record)

    db.commit()
    return {"message": "Student attendance saved"}

@router.post("/employees")
def mark_employee_attendance(
    data: EmployeeAttendanceCreate,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    employee = db.query(Employee).filter(
        Employee.id == data.employee_id,
        Employee.institute_id == user.institute_id
    ).first()

    if not employee:
        raise HTTPException(status_code=404)

    record = db.query(EmployeeAttendance).filter(
        EmployeeAttendance.employee_id == data.employee_id,
        EmployeeAttendance.date == data.date
    ).first()

    if record:
        record.status = data.status
    else:
        record = EmployeeAttendance(
            employee_id=data.employee_id,
            institute_id=user.institute_id,
            date=data.date,
            status=data.status
        )
        db.add(record)

    db.commit()
    return {"message": "Employee attendance saved"}
