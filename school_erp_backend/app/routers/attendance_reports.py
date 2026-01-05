from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

from app.database import get_db
from app.models.student_attendance import StudentAttendance
from app.models.employee_attendance import EmployeeAttendance
from app.models.student import Student
from app.models.employee import Employee
from app.dependencies import admin_or_superadmin, employee_permission_required
from reportlab.platypus import SimpleDocTemplate, Table
from fastapi.responses import FileResponse
import tempfile

router = APIRouter(prefix="/attendance-reports", tags=["Attendance Reports"])


@router.get("/students")
def student_attendance_report(
    start_date: date,
    end_date: date,
    class_name:str | None=Query(None),
    section: str | None = Query(None),
    db: Session = Depends(get_db),
    user=Depends(employee_permission_required("can_attendance"))
):
    q = db.query(
        StudentAttendance.student_id,
        Student.name,
        Student.class_name,
        Student.section,
        StudentAttendance.date,
        StudentAttendance.status
    ).join(Student,
    Student.id == StudentAttendance.student_id)

    if user.role != "superadmin":
        q = q.filter(StudentAttendance.institute_id == user.institute_id)
    
    if start_date and end_date:
        q = q.filter(StudentAttendance.date.between(start_date, end_date))

    if class_name:
        q = q.filter(Student.class_name == class_name)

    if section:
        q = q.filter(Student.section == section)

    q = q.order_by(StudentAttendance.date)

    # q = q.filter(
    #     StudentAttendance.date.between(start_date, end_date)
    # ).order_by(StudentAttendance.date)

    rows = q.all()

    return [
        {
            "student_id": r[0],
            "student_name": r[1],
            "class_name": r[2],
            "section": r[3],
            "date": r[4],
            "status": r[5]
        }
        for r in rows
    ]


@router.get("/employees")
def employee_attendance_report(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    q = db.query(
        EmployeeAttendance.employee_id,
        Employee.name,
        EmployeeAttendance.date,
        EmployeeAttendance.status
    ).join(Employee,
    Employee.id == EmployeeAttendance.employee_id)

    if user.role != "superadmin":
        q = q.filter(EmployeeAttendance.institute_id == user.institute_id)

    q = q.filter(
        EmployeeAttendance.date.between(start_date, end_date)
    ).order_by(EmployeeAttendance.date)

    rows = q.all()

    return [
        {
            "employee_id": r[0],
            "employee_name": r[1],
            "date": r[2],
            "status": r[3]
        }
        for r in rows
    ]


@router.get("/students/class-wise")
def class_wise_report(
    class_name: str = Query(...),
    section: str | None = Query(None),
    date_value: date = Query(...),
    db: Session = Depends(get_db),
    user=Depends(employee_permission_required("can_attendance"))
):
    q = db.query(
        StudentAttendance.student_id,
        Student.name,
        StudentAttendance.status
    ).join(Student,
    Student.id == StudentAttendance.student_id).filter(
        Student.class_name == class_name,
        StudentAttendance.date == date_value
    )

    if section:
        q = q.filter(Student.section == section)

    if user.role != "superadmin":
        q = q.filter(StudentAttendance.institute_id == user.institute_id)

    rows = q.all()

    return [
        {
            "student_id": r[0],
            "student_name": r[1],
            "status": r[2]
        }
        for r in rows
    ]

@router.get("/daily")
def daily_attendance_report(
    class_id: int,
    section_id: int | None = None,
    report_date: date = date.today(),
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    q = db.query(StudentAttendance).filter(
        StudentAttendance.institute_id == user.institute_id,
        StudentAttendance.class_id == class_id,
        StudentAttendance.date == report_date
    )

    if section_id:
        q = q.filter(StudentAttendance.section_id == section_id)

    records = q.all()

    total = len(records)
    present = sum(1 for r in records if r.status == "present")
    absent = total - present

    return {
        "date": report_date,
        "class_id": class_id,
        "section_id": section_id,
        "total": total,
        "present": present,
        "absent": absent,
        "percentage": round((present / total) * 100, 2) if total else 0
    }

@router.get("/monthly")
def monthly_attendance_report(
    class_id: int | None = Query(None),
    section_id: int | None = Query(None),
    month: str = Query(...),
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    q = db.query(
        StudentAttendance.status,
        func.count(StudentAttendance.id).label("count")
    ).filter(
        StudentAttendance.institute_id == user.institute_id,
        StudentAttendance.class_id == class_id,
        StudentAttendance.date.like(f"{month}%")
    )

    if section_id:
        q = q.filter(StudentAttendance.section_id == section_id)

    q = q.group_by(StudentAttendance.status)

    rows = q.all()

    # Default values (important!)
    result = {
        "present": 0,
        "absent": 0,
        "leave": 0
    }

    for status, count in rows:
        result[status] = count

    total = sum(result.values())

    return {
        "month": month,
        "class_id": class_id,
        "section_id": section_id,
        "total_entries": total,
        "present": result["present"],
        "absent": result["absent"],
        "leave": result["leave"],
        "attendance_percentage": round(
            (result["present"] / total) * 100, 2
        ) if total else 0
    }

# router.get("/monthly")
# def monthly_attendance_report(
#     class_id: int,
#     section_id: int | None,
#     month: str,  # YYYY-MM
#     db: Session = Depends(get_db),
#     user=Depends(admin_or_superadmin)
# ):
#     q = db.query(StudentAttendance).filter(
#         StudentAttendance.institute_id == user.institute_id,
#         StudentAttendance.class_id == class_id,
#         StudentAttendance.date.like(f"{month}%")
#     )

#     if section_id:
#         q = q.filter(StudentAttendance.section_id == section_id)

#     total_days = q.count()
#     present_days = q.filter(
#         StudentAttendance.status == "present"
#     ).count()

#     return {
#         "month": month,
#         "class_id": class_id,
#         "section_id": section_id,
#         "total_entries": total_days,
#         "present_entries": present_days,
#         "attendance_percentage": round(
#             (present_days / total_days) * 100, 2
#         ) if total_days else 0
#     }

@router.get("/students-snapshot")
def student_attendance_snapshot_report(
    class_id: int,
    section_id: int | None,
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
    user=Depends(employee_permission_required("can_attendance"))
):
    q = db.query(
        StudentAttendance.student_id,
        StudentAttendance.class_id,
        StudentAttendance.section_id,
        StudentAttendance.date,
        StudentAttendance.status
    ).filter(
        StudentAttendance.institute_id == user.institute_id,
        StudentAttendance.class_id == class_id,
        StudentAttendance.date.between(start_date, end_date)
    )

    if section_id:
        q = q.filter(StudentAttendance.section_id == section_id)

    rows = q.order_by(StudentAttendance.date).all()

    return [
        {
            "student_id": r.student_id,
            "class_id": r.class_id,
            "section_id": r.section_id,
            "date": r.date,
            "status": r.status
        }
        for r in rows
    ]
@router.get("/class-wise-snapshot")
def class_wise_snapshot_report(
    class_id: int,
    section_id: int | None,
    date_value: date,
    db: Session = Depends(get_db),
    user=Depends(employee_permission_required("can_attendance"))
):
    q = db.query(
        StudentAttendance.student_id,
        StudentAttendance.status
    ).filter(
        StudentAttendance.institute_id == user.institute_id,
        StudentAttendance.class_id == class_id,
        StudentAttendance.date == date_value
    )

    if section_id:
        q = q.filter(StudentAttendance.section_id == section_id)

    rows = q.all()

    return [
        {
            "student_id": r.student_id,
            "status": r.status
        }
        for r in rows
    ]
@router.get("/students/pdf")
def students_attendance_pdf(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    rows = db.query(
        Student.name,
        Student.class_name,
        StudentAttendance.date,
        StudentAttendance.status
    ).join(Student).filter(
        StudentAttendance.institute_id == user.institute_id,
        StudentAttendance.date.between(start_date, end_date)
    ).all()

    file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    doc = SimpleDocTemplate(file.name)
    table_data = [["Name", "Class", "Date", "Status"]]

    for r in rows:
        table_data.append([r[0], r[1], str(r[2]), r[3]])

    doc.build([Table(table_data)])

    return FileResponse(file.name, filename="attendance_report.pdf")
@router.get("/employees/monthly-summary")
def employee_monthly_summary(
    month: str = Query(..., description="Format: YYYY-MM"),
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    q = db.query(
        EmployeeAttendance.status,
        func.count(EmployeeAttendance.id).label("count")
    )

    # institute restriction
    if user.role != "superadmin":
        q = q.filter(EmployeeAttendance.institute_id == user.institute_id)

    # month filter
    q = q.filter(EmployeeAttendance.date.like(f"{month}%"))

    q = q.group_by(EmployeeAttendance.status)

    rows = q.all()

    # default result (important for bar chart)
    result = {
        "present": 0,
        "absent": 0,
        "leave": 0
    }

    for status, count in rows:
        result[status] = count

    total = sum(result.values())

    return {
        "month": month,
        "total_entries": total,
        "present": result["present"],
        "absent": result["absent"],
        "leave": result["leave"]
    }
