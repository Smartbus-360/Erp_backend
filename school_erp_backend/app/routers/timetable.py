from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.timetable import Timetable
from app.models.weekday import Weekday
from app.models.class_model import SchoolClass
from app.models.employee import Employee
from app.schemas.timetable_schema import (
    TimetableCreate,
    TimetableResponse
)
from app.dependencies import employee_permission_required
from app.auth import get_current_user
from fastapi.responses import StreamingResponse
from app.services.timetable_pdf import generate_timetable_pdf
from app.models.period import Period
from app.models.weekday import Weekday
from app.models.subject import Subject
from app.models.employee import Employee
from app.dependencies import admin_or_superadmin
from app.models.class_model import SchoolClass
from app.models.section import Section

router = APIRouter(prefix="/timetable", tags=["Timetable"])

@router.post("/", response_model=TimetableResponse)
def add_or_update_period(
    data: TimetableCreate,
    db: Session = Depends(get_db),
    user=Depends(employee_permission_required("can_timetable"))
):
    # Validate weekday
    weekday = db.query(Weekday).filter(
        Weekday.id == data.weekday_id,
        Weekday.institute_id == user.institute_id,
        Weekday.is_active == True
    ).first()

    if not weekday:
        raise HTTPException(400, "Invalid weekday")

    # Validate teacher
    teacher = db.query(Employee).filter(
        Employee.id == data.teacher_id,
        Employee.institute_id == user.institute_id
    ).first()

    if not teacher:
        raise HTTPException(400, "Invalid teacher")

    # Prevent duplicate slot
    record = db.query(Timetable).filter(
        Timetable.institute_id == user.institute_id,
        Timetable.class_id == data.class_id,
        Timetable.section_id == data.section_id,
        Timetable.weekday_id == data.weekday_id,
        Timetable.period_no == data.period_no
    ).first()

    # ❌ Teacher conflict check
    conflict = db.query(Timetable).filter(
    Timetable.institute_id == user.institute_id,
    Timetable.teacher_id == data.teacher_id,
    Timetable.weekday_id == data.weekday_id,
    Timetable.period_no == data.period_no,
    Timetable.id != (record.id if record else None)
    ).first()

    if conflict:
        raise HTTPException(
        status_code=400,
        detail="Teacher already assigned in another class at this time"
    )


    if record:
        record.subject_id = data.subject_id
        record.teacher_id = data.teacher_id
    else:
        record = Timetable(
            **data.dict(),
            institute_id=user.institute_id
        )
        db.add(record)

    db.commit()
    db.refresh(record)
    return record

# @router.get("/", response_model=list[TimetableResponse])
# def get_timetable(
#     class_id: int,
#     section_id: int | None = None,
#     db: Session = Depends(get_db),
#     user=Depends(employee_permission_required("can_timetable"))
# ):
#     q = db.query(Timetable).filter(
#         Timetable.institute_id == user.institute_id,
#         Timetable.class_id == class_id
#     )

#     if section_id:
#         q = q.filter(Timetable.section_id == section_id)

#     return q.order_by(
#         Timetable.weekday_id,
#         Timetable.period_no
#     ).all()

@router.get("/")
def get_timetable(
    class_id: int   |  None=None,
    section_id: int | None = None,
    teacher_id: int | None = None,
    db: Session = Depends(get_db),
    user=Depends(employee_permission_required("can_timetable"))
):
    q = (
        db.query(
            Timetable,
            Subject.name.label("subject_name"),
            Employee.name.label("teacher_name"),
            SchoolClass.name.label("class_name"),
            Section.name.label("section_name"),

        )
        .join(Subject, Subject.id == Timetable.subject_id)
        .join(Employee, Employee.id == Timetable.teacher_id)
        .join(SchoolClass, SchoolClass.id == Timetable.class_id)
        .join(Section, Section.id == Timetable.section_id)
        .filter(
            Timetable.institute_id == user.institute_id,
            # Timetable.class_id == class_id
        )
    )

    if section_id:
        q = q.filter(Timetable.section_id == section_id)
    
    if class_id:
        q = q.filter(Timetable.class_id == class_id)

    # if section_id:
    #     q = q.filter(Timetable.section_id == section_id)

    if teacher_id:
        q = q.filter(Timetable.teacher_id == teacher_id)


    results = []
    for t, subject_name, teacher_name,class_name,section_name in q.order_by(
        Timetable.weekday_id,
        Timetable.period_no
    ).all():
        results.append({
            "id": t.id,
            "class_id": t.class_id,
            "section_id": t.section_id,
            "weekday_id": t.weekday_id,
            "period_no": t.period_no,
            "subject_id": t.subject_id,
            "teacher_id": t.teacher_id,
            "class_name": class_name,
            "section_name": section_name,
            "subject_name": subject_name,
            "teacher_name": teacher_name
        })

    return results


@router.post("/weekdays")
def add_weekday(name: str, db: Session = Depends(get_db), user=Depends(admin_or_superadmin)):
    db.add(Weekday(name=name, institute_id=user.institute_id))
    db.commit()
    return {"message": "Weekday added"}

@router.get("/teacher", response_model=list[TimetableResponse])
def teacher_timetable(
    db: Session = Depends(get_db),
    user=Depends(employee_permission_required("can_timetable"))
):
    # Resolve employee
    teacher = db.query(Employee).filter(
        Employee.user_id == user.id,
        Employee.institute_id == user.institute_id
    ).first()

    if not teacher:
        raise HTTPException(status_code=403, detail="Teacher not found")

    return db.query(Timetable).filter(
        Timetable.teacher_id == teacher.id,
        Timetable.institute_id == user.institute_id
    ).order_by(
        Timetable.weekday_id,
        Timetable.period_no
    ).all()
@router.get("/student", response_model=list[TimetableResponse])
def student_timetable(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role != "student":
        raise HTTPException(status_code=403)

    student = db.query(Student).filter(
        Student.user_id == user.id,
        Student.institute_id == user.institute_id
    ).first()

    if not student:
        return []

    return db.query(Timetable).filter(
        Timetable.institute_id == user.institute_id,
        Timetable.class_id == student.class_id,
        (Timetable.section_id == student.section_id) |
        (Timetable.section_id == None)
    ).order_by(
        Timetable.weekday_id,
        Timetable.period_no
    ).all()

@router.get("/export/class")
def export_class_timetable_pdf(
    class_id: int,
    section_id: int | None = None,
    db: Session = Depends(get_db),
    user=Depends(employee_permission_required("can_timetable"))
):
    # Fetch periods
    periods = db.query(Period).filter(
        Period.institute_id == user.institute_id
    ).order_by(Period.order_no).all()

    # Fetch weekdays
    weekdays = db.query(Weekday).filter(
        Weekday.institute_id == user.institute_id,
        Weekday.is_active == True
    ).all()

    timetable = db.query(Timetable).filter(
        Timetable.institute_id == user.institute_id,
        Timetable.class_id == class_id,
        (Timetable.section_id == section_id) |
        (Timetable.section_id == None)
    ).all()

    # Build matrix
    matrix = {}
    for wd in weekdays:
        row = []
        for p in periods:
            slot = next(
                (
                    t for t in timetable
                    if t.weekday_id == wd.id and t.period_no == p.order_no
                ),
                None
            )

            if slot:
                subject = db.query(Subject).get(slot.subject_id)
                teacher = db.query(Employee).get(slot.teacher_id)
                row.append(f"{subject.name}\n({teacher.name})")
            else:
                row.append("-")

        matrix[wd.name] = row

    pdf_buffer = generate_timetable_pdf(
        school_name="School Timetable",
        title=f"Class {class_id} Section {section_id or 'All'}",
        periods=[
            {
                "name": p.name,
                "time": f"{p.start_time}-{p.end_time}"
            } for p in periods
        ],
        timetable_matrix=matrix
    )

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            "attachment; filename=timetable.pdf"
        }
    )

