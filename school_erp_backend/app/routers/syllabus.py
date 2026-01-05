from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.syllabus import Syllabus
from app.models.employee import Employee
from app.schemas.syllabus_schema import (
    SyllabusCreate,
    SyllabusResponse
)
from app.dependencies import employee_permission_required
from fastapi import UploadFile, File, Form
from app.models.subject import Subject

router = APIRouter(prefix="/syllabus", tags=["Syllabus"])

@router.post("/", response_model=SyllabusResponse)
def add_or_update_syllabus(
    data: SyllabusCreate,
    db: Session = Depends(get_db),
    user=Depends(employee_permission_required("can_syllabus"))
):
    # Validate teacher
    teacher = db.query(Employee).filter(
        Employee.id == data.teacher_id,
        Employee.institute_id == user.institute_id
    ).first()

    if not teacher:
        raise HTTPException(400, "Invalid teacher")

    # Prevent duplicate syllabus
    syllabus = db.query(Syllabus).filter(
        Syllabus.institute_id == user.institute_id,
        Syllabus.class_id == data.class_id,
        Syllabus.section_id == data.section_id,
        Syllabus.subject_id == data.subject_id
    ).first()

    if syllabus:
        syllabus.title = data.title
        syllabus.description = data.description
        syllabus.teacher_id = data.teacher_id
    else:
        syllabus = Syllabus(
            **data.dict(),
            institute_id=user.institute_id
        )
        db.add(syllabus)

    db.commit()
    db.refresh(syllabus)
    return syllabus

# @router.get("/", response_model=list[SyllabusResponse])
# def get_syllabus(
#     class_id: int,
#     section_id: int | None = None,
#     db: Session = Depends(get_db),
#     user=Depends(employee_permission_required("can_view_syllabus"))
# ):
#     q = db.query(Syllabus).filter(
#         Syllabus.institute_id == user.institute_id,
#         Syllabus.class_id == class_id
#     )

#     # Section override priority
#     if section_id:
#         q = q.filter(
#             (Syllabus.section_id == section_id) |
#             (Syllabus.section_id == None)
#         )

#     return q.all()
@router.get("/", response_model=list[SyllabusResponse])
def get_syllabus(
    class_id: int,
    section_id: int | None = None,
    db: Session = Depends(get_db),
    user=Depends(employee_permission_required("can_view_syllabus"))
):
    q = (
        db.query(
            Syllabus,
            Subject.name.label("subject_name")
        )
        .join(Subject, Subject.id == Syllabus.subject_id)
        .filter(
            Syllabus.institute_id == user.institute_id,
            Syllabus.class_id == class_id
        )
    )

    if section_id:
        q = q.filter(
            (Syllabus.section_id == section_id) |
            (Syllabus.section_id == None)
        )

    results = []
    for s, subject_name in q.all():
        results.append({
            "id": s.id,
            "class_id": s.class_id,
            "section_id": s.section_id,
            "subject_id": s.subject_id,
            "subject_name": subject_name,   # ✅ now available
            "teacher_id": s.teacher_id,
            "title": s.title,
            "description": s.description
        })

    return results


@router.post("/upload")
def upload_syllabus_image(
    syllabus_id: int = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(employee_permission_required("can_syllabus"))
):
    syllabus = db.query(Syllabus).filter(
        Syllabus.id == syllabus_id,
        Syllabus.institute_id == user.institute_id
    ).first()

    if not syllabus:
        raise HTTPException(404, "Syllabus not found")

    syllabus.image = image.filename
    db.commit()

    return {"message": "Image uploaded"}
