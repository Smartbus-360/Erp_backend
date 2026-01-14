from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.subject import Subject
from app.models.class_subject import ClassSubject
from app.models.class_model import SchoolClass
from app.schemas.subject_schema import (
    SubjectCreate,
    AssignSubject,
    SubjectResponse
)
from app.dependencies import admin_or_superadmin
from app.auth import get_current_user
from sqlalchemy import func
from app.models.employee import Employee

router = APIRouter(prefix="/subjects", tags=["Subjects"])

@router.post("/", response_model=SubjectResponse)
def create_subject(
    data: SubjectCreate,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    exists = db.query(Subject).filter(
        Subject.name == data.name,
        Subject.institute_id == user.institute_id
    ).first()

    if exists:
        raise HTTPException(status_code=400, detail="Subject already exists")

    subject = Subject(
        name=data.name,
        institute_id=user.institute_id
    )

    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject

@router.get("/", response_model=list[SubjectResponse])
def list_subjects(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role == "superadmin":
        return db.query(Subject).all()

    return db.query(Subject).filter(
        Subject.institute_id == user.institute_id
    ).all()

@router.post("/assign")
def assign_subjects_to_class(
    data: AssignSubject,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    cls = db.query(SchoolClass).filter(
        SchoolClass.id == data.class_id,
        SchoolClass.institute_id == user.institute_id
    ).first()

    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")

    # Clear old mappings
    # db.query(ClassSubject).filter(
    #     ClassSubject.class_id == data.class_id
    # ).delete()

    # Add new mappings (without deleting old ones)
    for subject_id in data.subject_ids:
        exists = db.query(ClassSubject).filter(
            ClassSubject.class_id == data.class_id,
            ClassSubject.subject_id == subject_id,
            ClassSubject.institute_id == user.institute_id
    ).first()

        if not exists:
            cs = ClassSubject(
            class_id=data.class_id,
            subject_id=subject_id,
            institute_id=user.institute_id
        )
            db.add(cs)

    db.commit()
    return {"message": "Subjects assigned successfully"}
    

    # Add new mappings
    # for subject_id in data.subject_ids:
    #     cs = ClassSubject(
    #         class_id=data.class_id,
    #         subject_id=subject_id,
    #         institute_id=user.institute_id
    #     )
    #     db.add(cs)

    # db.commit()
    # return {"message": "Subjects assigned successfully"}


@router.get("/class/{class_id}", response_model=list[SubjectResponse])
def subjects_by_class(
    class_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    q = db.query(Subject).join(
        ClassSubject,
        Subject.id == ClassSubject.subject_id
    ).filter(
        ClassSubject.class_id == class_id
    )

    if user.role != "superadmin":
        q = q.filter(ClassSubject.institute_id == user.institute_id)

    return q.all()

@router.get("/by-name", response_model=SubjectResponse)
def get_subject_by_name(
    name: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    subject = db.query(Subject).filter(
        Subject.name.ilike(name),
        Subject.institute_id == user.institute_id
    ).first()

    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    return subject

@router.get("/assigned/{class_id}")
def get_assigned_subjects(
    class_id: int,
    section_id: int | None = None,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    q = (
        db.query(Subject, ClassSubject)
        .join(ClassSubject, Subject.id == ClassSubject.subject_id)
        .filter(
            ClassSubject.class_id == class_id,
            ClassSubject.institute_id == user.institute_id
        )
    )

    results = []
    for subject, cs in q.all():
        results.append({
            "id": subject.id,
            "name": subject.name
        })

    return results

@router.get("/summary")
def subject_summary(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    rows = (
        db.query(
            SchoolClass.id.label("class_id"),
            SchoolClass.name.label("class_name"),
            func.count(func.distinct(ClassSubject.subject_id)).label("total_subjects")
        )
        .join(ClassSubject, ClassSubject.class_id == SchoolClass.id)
        .filter(ClassSubject.institute_id == user.institute_id)
        .group_by(SchoolClass.id, SchoolClass.name)
        .all()
    )

    # 🔥 CRITICAL FIX: convert to dict
    return [
        {
            "class_id": r.class_id,
            "class_name": r.class_name,
            "total_subjects": r.total_subjects
        }
        for r in rows
    ]


@router.get("/details/{class_id}")
def subjects_with_teachers(
    class_id: int,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    rows = (
        db.query(
            Subject.id,
            Subject.name.label("subject_name"),
            Employee.name.label("teacher_name")
        )
        .join(ClassSubject, ClassSubject.subject_id == Subject.id)
        .outerjoin(Employee, Employee.id == ClassSubject.teacher_id)
        .filter(
            ClassSubject.class_id == class_id,
            ClassSubject.institute_id == user.institute_id
        )
        .all()
    )

    return [
        {
            "subject_id": r.id,
            "subject_name": r.subject_name,
            "teacher_name": r.teacher_name or "Not Assigned"
        }
        for r in rows
    ]
