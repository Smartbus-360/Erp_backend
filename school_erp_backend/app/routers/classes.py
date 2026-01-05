from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.class_model import SchoolClass
from app.models.section import Section
from app.schemas.class_schema import (
    ClassCreate,
    SectionCreate,
    ClassResponse,
    SectionResponse
)
from app.dependencies import admin_or_superadmin
from app.auth import get_current_user
from sqlalchemy import func
from app.models.section import Section
from app.models.student import Student
from app.models.employee import Employee

router = APIRouter(prefix="/classes", tags=["Classes"])

@router.post("/", response_model=ClassResponse)
def create_class(
    data: ClassCreate,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    exists = db.query(SchoolClass).filter(
        SchoolClass.name == data.name,
        SchoolClass.institute_id == user.institute_id
    ).first()

    if exists:
        raise HTTPException(status_code=400, detail="Class already exists")

    cls = SchoolClass(
        name=data.name,
        institute_id=user.institute_id,
        class_teacher_id=data.class_teacher_id
    )

    db.add(cls)
    db.commit()
    db.refresh(cls)
    return cls

# @router.get("/", response_model=list[ClassResponse])
@router.get("/")
def list_classes(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role == "superadmin":
        return db.query(SchoolClass).all()

    # return db.query(SchoolClass).filter(
    #     SchoolClass.institute_id == user.institute_id
    # ).all()
    q = (
        db.query(
            SchoolClass.id,
            SchoolClass.name,
            Employee.name.label("teacher_name"),
            func.count(func.distinct(Section.id)).label("sections_count"),
            func.count(func.distinct(Student.id)).label("students_count"),
        )
        .outerjoin(Employee, Employee.id == SchoolClass.class_teacher_id)
        .outerjoin(Section, Section.class_id == SchoolClass.id)
        .outerjoin(Student, Student.class_id == SchoolClass.id)
        .filter(SchoolClass.institute_id == user.institute_id)
        .group_by(SchoolClass.id, Employee.name)
    )

    return [
        {
        "id": c.id,
        "name": c.name,
        "teacher_name": c.teacher_name,
        "sections_count": c.sections_count,
        "students_count": c.students_count,
        }
        for c in q.all()
    ]


@router.post("/sections", response_model=SectionResponse)
def add_section(
    data: SectionCreate,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    cls = db.query(SchoolClass).filter(
        SchoolClass.id == data.class_id,
        SchoolClass.institute_id == user.institute_id
    ).first()

    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")

    exists = db.query(Section).filter(
        Section.name == data.name,
        Section.class_id == data.class_id
    ).first()

    if exists:
        raise HTTPException(status_code=400, detail="Section already exists")

    sec = Section(
        name=data.name,
        class_id=data.class_id,
        institute_id=user.institute_id
    )

    db.add(sec)
    db.commit()
    db.refresh(sec)
    return sec

@router.get("/{class_id}/sections", response_model=list[SectionResponse])
def list_sections(
    class_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return db.query(Section).filter(
        Section.class_id == class_id,
        Section.institute_id == user.institute_id
    ).all()

# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session

# from app.database import get_db
# from app.models.class_model import SchoolClass
# from app.models.section import Section
# from app.schemas.class_schema import (
#     ClassCreate,
#     SectionCreate,
#     ClassResponse,
#     SectionResponse
# )
# from app.dependencies import admin_or_superadmin
# from app.auth import get_current_user

# router = APIRouter(prefix="/classes", tags=["Classes"])

# @router.post("/", response_model=ClassResponse)
# def create_class(
#     data: ClassCreate,
#     db: Session = Depends(get_db),
#     user=Depends(admin_or_superadmin)
# ):
#     exists = db.query(SchoolClass).filter(
#         SchoolClass.name == data.name,
#         SchoolClass.institute_id == user.institute_id
#     ).first()

#     if exists:
#         raise HTTPException(status_code=400, detail="Class already exists")

#     cls = SchoolClass(
#         name=data.name,
#         institute_id=user.institute_id
#     )

#     db.add(cls)
#     db.commit()
#     db.refresh(cls)
#     return cls

# @router.get("/", response_model=list[ClassResponse])
# def list_classes(
#     db: Session = Depends(get_db),
#     user=Depends(get_current_user)
# ):
#     if user.role == "superadmin":
#         return db.query(SchoolClass).all()

#     return db.query(SchoolClass).filter(
#         SchoolClass.institute_id == user.institute_id
#     ).all()

# @router.post("/sections", response_model=SectionResponse)
# def add_section(
#     data: SectionCreate,
#     db: Session = Depends(get_db),
#     user=Depends(admin_or_superadmin)
# ):
#     cls = db.query(SchoolClass).filter(
#         SchoolClass.id == data.class_id,
#         SchoolClass.institute_id == user.institute_id
#     ).first()

#     if not cls:
#         raise HTTPException(status_code=404, detail="Class not found")

#     exists = db.query(Section).filter(
#         Section.name == data.name,
#         Section.class_id == data.class_id
#     ).first()

#     if exists:
#         raise HTTPException(status_code=400, detail="Section already exists")

#     sec = Section(
#         name=data.name,
#         class_id=data.class_id,
#         institute_id=user.institute_id
#     )

#     db.add(sec)
#     db.commit()
#     db.refresh(sec)
#     return sec

# @router.get("/{class_id}/sections", response_model=list[SectionResponse])
# def list_sections(
#     class_id: int,
#     db: Session = Depends(get_db),
#     user=Depends(get_current_user)
# ):
#     return db.query(Section).filter(
#         Section.class_id == class_id,
#         Section.institute_id == user.institute_id
#     ).all()


# @router.get("/classes/{class_id}")
# def get_class(class_id: int, db: Session = Depends(get_db)):
#     cls = db.query(Class).filter(Class.id == class_id).first()

#     sections = db.query(Section).filter(Section.class_id == class_id).all()

#     return {
#         "id": cls.id,
#         "name": cls.name,
#         "class_teacher_id": cls.class_teacher_id,
#         "sections": [{"id": s.id, "name": s.name} for s in sections],
#         "monthly_fee": cls.monthly_fee
#     }

# @router.get("/{class_id}")
# def get_class(class_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
#     cls = db.query(SchoolClass).filter(
#         SchoolClass.id == class_id,
#         SchoolClass.institute_id == user.institute_id
#     ).first()

#     if not cls:
#         raise HTTPException(404, "Class not found")

#     return cls

@router.get("/{class_id}")
def get_class(class_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    cls = db.query(SchoolClass).filter(
        SchoolClass.id == class_id,
        SchoolClass.institute_id == user.institute_id
    ).first()

    if not cls:
        raise HTTPException(404, "Class not found")

    sections = db.query(Section).filter(
        Section.class_id == class_id
    ).all()

    return {
        "id": cls.id,
        "name": cls.name,
        "class_teacher_id": cls.class_teacher_id,
        "sections": [{"id": s.id, "name": s.name} for s in sections],
        "monthly_fee": None
    }

@router.put("/{class_id}")
def update_class(
    class_id: int,
    data: ClassCreate,
    db: Session = Depends(get_db),
    user=Depends(admin_or_superadmin)
):
    cls = db.query(SchoolClass).filter(
        SchoolClass.id == class_id,
        SchoolClass.institute_id == user.institute_id
    ).first()

    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")

    cls.name = data.name
    cls.class_teacher_id = data.class_teacher_id

    db.commit()
    db.refresh(cls)

    return cls
