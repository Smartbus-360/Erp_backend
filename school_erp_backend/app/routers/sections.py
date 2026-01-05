from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.section import Section
from app.auth import get_current_user
from app.dependencies import admin_or_superadmin

router = APIRouter(
    prefix="/sections",
    tags=["Sections"]
)


@router.post("/", dependencies=[Depends(admin_or_superadmin)])
def create_section(
    data: dict,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    name = data.get("name")
    class_id = data.get("class_id")

    if not name or not class_id:
        raise HTTPException(400, "name and class_id required")

    # prevent duplicate section in same class
    existing = db.query(Section).filter(
        Section.name == name,
        Section.class_id == class_id,
        Section.institute_id == user.institute_id
    ).first()

    if existing:
        raise HTTPException(400, "Section already exists")

    section = Section(
        name=name,
        class_id=class_id,
        institute_id=user.institute_id
    )

    db.add(section)
    db.commit()
    db.refresh(section)

    return {
        "id": section.id,
        "name": section.name,
        "class_id": section.class_id
    }


@router.get("/", dependencies=[Depends(admin_or_superadmin)])
def list_sections(
    class_id: int | None = None,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    q = db.query(Section).filter(
        Section.institute_id == user.institute_id
    )

    if class_id:
        q = q.filter(Section.class_id == class_id)

    return q.all()

@router.get("/by-class/{class_id}")
def sections_by_class(
    class_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return db.query(Section).filter(
        Section.class_id == class_id,
        Section.institute_id == user.institute_id
    ).all()
