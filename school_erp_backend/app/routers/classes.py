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
from sqlalchemy import func , case
from app.models.section import Section
from app.models.student import Student
from app.models.employee import Employee
from app.routers.fees import calculate_fees_stats


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
# @router.get("/")
# def list_classes(
#     db: Session = Depends(get_db),
#     user=Depends(get_current_user)
# ):
#     if user.role == "superadmin":
#         return db.query(SchoolClass).all()

#     # return db.query(SchoolClass).filter(
#     #     SchoolClass.institute_id == user.institute_id
#     # ).all()
#     q = (
#         db.query(
#             SchoolClass.id,
#             SchoolClass.name,
#             Employee.name.label("teacher_name"),
#             func.count(func.distinct(Section.id)).label("sections_count"),
#             func.count(func.distinct(Student.id)).label("students_count"),
#         )
#         .outerjoin(Employee, Employee.id == SchoolClass.class_teacher_id)
#         .outerjoin(Section, Section.class_id == SchoolClass.id)
#         .outerjoin(Student, Student.class_id == SchoolClass.id)
#         .filter(SchoolClass.institute_id == user.institute_id)
#         .group_by(SchoolClass.id, Employee.name)
#     )

#     return [
#         {
#         "id": c.id,
#         "name": c.name,
#         "teacher_name": c.teacher_name,
#         "sections_count": c.sections_count,
#         "students_count": c.students_count,
#         }
#         for c in q.all()
#     ]

# @router.get("/")
# def list_classes(
#     db: Session = Depends(get_db),
#     user=Depends(get_current_user)
# ):
#     classes = db.query(SchoolClass).filter(
#         SchoolClass.institute_id == user.institute_id
#     ).all()

#     result = []

#     for cls in classes:
#         students = db.query(Student).filter(
#             Student.class_id == cls.id
#         ).all()

#         total = len(students)
#         boys = sum(1 for s in students if s.gender == "male")
#         girls = sum(1 for s in students if s.gender == "female")

#         boys_percent = round((boys / total) * 100) if total else 0
#         girls_percent = round((girls / total) * 100) if total else 0

#         sections = db.query(Section).filter(
#             Section.class_id == cls.id
#         ).all()

#         section_data = []
#         for sec in sections:
#             sec_students = [s for s in students if s.section == sec.name]

#             section_data.append({
#                 "name": sec.name,
#                 "total": len(sec_students),
#                 "boys": sum(1 for s in sec_students if s.gender == "male"),
#                 "girls": sum(1 for s in sec_students if s.gender == "female"),
#             })

#         teacher = db.query(Employee).filter(
#             Employee.id == cls.class_teacher_id
#         ).first()

#         result.append({
#             "id": cls.id,
#             "name": cls.name,
#             "teacher_name": teacher.name if teacher else None,
#             "students_count": total,
#             "sections_count": len(sections),

#             "boys_count": boys,
#             "girls_count": girls,
#             "boys_percent": boys_percent,
#             "girls_percent": girls_percent,

#             "sections": section_data
#         })

#     return result

@router.get("/")
def list_classes(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    classes = (
        db.query(SchoolClass)
        .filter(SchoolClass.institute_id == user.institute_id)
        .all()
    )

    response = []

    for cls in classes:

        total_students = (
            db.query(func.count(Student.id))
            .filter(Student.class_id == cls.id)
            .scalar()
        ) or 0

        boys = (
            db.query(func.count(Student.id))
            .filter(
                Student.class_id == cls.id,
                Student.gender == "male"
            )
            .scalar()
        ) or 0

        girls = (
            db.query(func.count(Student.id))
            .filter(
                Student.class_id == cls.id,
                Student.gender == "female"
            )
            .scalar()
        ) or 0

        boys_percent = round((boys / total_students) * 100) if total_students else 0
        girls_percent = round((girls / total_students) * 100) if total_students else 0

        # 🟣 CASTE STATS (CLASS LEVEL)
        caste_rows = (
            db.query(
                Student.caste,
                func.count(Student.id)
            )
            .filter(Student.class_id == cls.id)
            .group_by(Student.caste)
            .all()
        )

        caste_stats = {
            caste: round((count / total_students) * 100)
            for caste, count in caste_rows
        } if total_students else {}

        fees_stats = calculate_fees_stats(
            db=db,
            institute_id=user.institute_id,
            class_id=cls.id
        )


        # 🟢 SECTIONS (SUMMARY ONLY, NO STUDENTS)
        sections = (
            db.query(Section)
            .filter(Section.class_id == cls.id)
            .all()
        )

        section_list = []
        for sec in sections:
            sec_total = (
                db.query(func.count(Student.id))
                .filter(
                    Student.class_id == cls.id,
                    Student.section == sec.name
                )
                .scalar()
            ) or 0

            section_list.append({
                "id": sec.id,
                "name": sec.name,
                "total": sec_total
            })

        response.append({
            "id": cls.id,
            "name": cls.name,
            "teacher_name": (
                db.query(Employee.name)
                .filter(Employee.id == cls.class_teacher_id)
                .scalar()
            ),
            "students_count": total_students,
            "boys_percent": boys_percent,
            "girls_percent": girls_percent,
            "caste_stats": caste_stats,
            "fees_stats": fees_stats,
            "sections": section_list,
            "sections_count": len(section_list)
        })

    return response

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

@router.get("/{class_id}/sections/summary")
def section_summary(
    class_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    sections = (
        db.query(Section)
        .filter(
            Section.class_id == class_id,
            Section.institute_id == user.institute_id
        )
        .all()
    )

    result = []

    for sec in sections:
        total = (
            db.query(func.count(Student.id))
            .filter(
                Student.class_id == class_id,
                Student.section == sec.name
            )
            .scalar()
        ) or 0

        boys = (
            db.query(func.count(Student.id))
            .filter(
                Student.class_id == class_id,
                Student.section == sec.name,
                Student.gender == "male"
            )
            .scalar()
        ) or 0

        girls = (
            db.query(func.count(Student.id))
            .filter(
                Student.class_id == class_id,
                Student.section == sec.name,
                Student.gender == "female"
            )
            .scalar()
        ) or 0

        caste_rows = (
            db.query(
                Student.caste,
                func.count(Student.id)
            )
            .filter(
                Student.class_id == class_id,
                Student.section == sec.name
            )
            .group_by(Student.caste)
            .all()
        )

        caste_stats = {
            caste: round((count / total) * 100,1)
            for caste, count in caste_rows
        } if total else {}

        fees_stats = calculate_fees_stats(
            db=db,
            institute_id=user.institute_id,
            class_id=class_id,
            section=sec.name
        )


        result.append({
            "id": sec.id,
            "name": sec.name,
            "students_count": total,
            "boys_percent": round((boys / total) * 100) if total else 0,
            "girls_percent": round((girls / total) * 100) if total else 0,
            "caste_stats": caste_stats,
            "fees_stats": fees_stats   # ✅ ADD THIS LINE

        })

    return result
