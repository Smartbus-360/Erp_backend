from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.homework import Homework
from app.schemas.homework_schema import HomeworkCreate, HomeworkResponse
from app.dependencies import employee_permission_required
from app.auth import get_current_user
from app.models.student import Student
from app.models.class_model import SchoolClass
from datetime import date
from typing import Optional
from app.models.employee import Employee
from app.models.subject import Subject
from app.dependencies import admin_or_superadmin

router = APIRouter(prefix="/homework", tags=["Homework"])


@router.post("/", response_model=HomeworkResponse)
def add_homework(
    data: HomeworkCreate,
    db: Session = Depends(get_db),
    user=Depends(employee_permission_required("can_homework"))
):
    # hw = Homework(
    #     **data.dict(),
    #     teacher_id=user.id,
    #     institute_id=user.institute_id
    # )
    hw = Homework(
    class_id=data.class_id,
    subject_id=data.subject_id,
    teacher_id=data.teacher_id or user.id,
    title=data.title,
    description=data.description,
    due_date=data.due_date,
    institute_id=user.institute_id
)


    db.add(hw)
    db.commit()
    db.refresh(hw)
    return hw

# @router.get("/", response_model=list[HomeworkResponse])
# @router.get("/")
# def list_homework(
#     homework_date: Optional[date] = None,
#     class_id: Optional[int] = None,
#     teacher_id: Optional[int] = None,
#     db: Session = Depends(get_db),
#     user=Depends(employee_permission_required("can_homework"))
# ):
#     q = db.query(
#         Homework,
#         SchoolClass.name.label("class_name"),
#         Subject.name.label("subject_name"),
#         Employee.name.label("teacher_name")
#     ).join(
#         SchoolClass, SchoolClass.id == Homework.class_id
#     ).join(
#         Subject, Subject.id == Homework.subject_id
#     ).outerjoin(Employee, Employee.id == Homework.teacher_id)
#     .filter(
#         Homework.institute_id == user.institute_id
#     )

#     if homework_date:
#         q = q.filter(Homework.due_date == homework_date)

#     if class_id:
#         q = q.filter(Homework.class_id == class_id)

#     if teacher_id:
#         q = q.filter(Homework.teacher_id == teacher_id)

#     result = []
#     for hw, class_name, subject_name, teacher_name in q.all():
#         result.append({
#             "id": hw.id,
#             "class_id": hw.class_id,
#             "class_name": class_name,
#             "subject_id": hw.subject_id,
#             "subject_name": subject_name,
#             "teacher_id": hw.teacher_id,
#             "teacher_name": teacher_name,
#             "title": hw.title,
#             "description": hw.description,
#             "due_date": hw.due_date
#         })

#     return result

@router.get("/")
def list_homework(
    homework_date: Optional[date] = None,
    class_id: Optional[int] = None,
    teacher_id: Optional[int] = None,
    db: Session = Depends(get_db),
user=Depends(admin_or_superadmin)
):
    q = db.query(
        Homework,
        SchoolClass.name.label("class_name"),
        Subject.name.label("subject_name"),
        Employee.name.label("teacher_name")
    ).join(
        SchoolClass, SchoolClass.id == Homework.class_id
    ).join(
        Subject, Subject.id == Homework.subject_id
    ).outerjoin(   # ✅ IMPORTANT CHANGE
        Employee, Employee.id == Homework.teacher_id
    ).filter(
        Homework.institute_id == user.institute_id
    )

    if homework_date:
        q = q.filter(Homework.due_date == homework_date)

    if class_id:
        q = q.filter(Homework.class_id == class_id)

    if teacher_id:
        q = q.filter(Homework.teacher_id == teacher_id)

    result = []
    for hw, class_name, subject_name, teacher_name in q.all():
        result.append({
            "id": hw.id,
            "class_id": hw.class_id,
            "class_name": class_name,
            "subject_id": hw.subject_id,
            "subject_name": subject_name,
            "teacher_id": hw.teacher_id,
            "teacher_name": teacher_name or "Admin",  # ✅ fallback
            "title": hw.title,
            "description": hw.description,
            "due_date": hw.due_date
        })

    return result

# @router.get("/", response_model=list[HomeworkResponse])
# def list_homework(
#     db: Session = Depends(get_db),
#     user=Depends(employee_permission_required("can_homework"))
# ):
#     return db.query(Homework).filter(
#         Homework.institute_id == user.institute_id
#     ).order_by(Homework.due_date.desc()).all()

@router.get("/me", response_model=list[HomeworkResponse])
def student_homework(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role != "student":
        raise HTTPException(status_code=403, detail="Forbidden")

    # 1. Get student profile
    student = db.query(Student).filter(
        Student.user_id == user.id,
        Student.institute_id == user.institute_id
    ).first()

    if not student:
        return []

    # 2. Resolve class
    cls = db.query(SchoolClass).filter(
        SchoolClass.name == student.class_name,
        SchoolClass.institute_id == user.institute_id
    ).first()

    if not cls:
        return []

    # 3. Fetch homework
    return db.query(Homework).filter(
        Homework.class_id == cls.id,
        Homework.institute_id == user.institute_id,
        (
            (Homework.section_id == student.section_id) |
            (Homework.section_id == None)
        )
    ).order_by(Homework.due_date.desc()).all()
