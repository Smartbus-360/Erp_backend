from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.institute import Institute
from app.models.user import User
from app.schemas.institute import (
    InstituteCreate,
    InstituteResponse,
    AdminCreate,
    InstituteUpdate
)
from app.dependencies import superadmin_only
from app.security import hash_password
from app.auth import get_current_user

router = APIRouter(prefix="/institutes", tags=["Institutes"])


@router.post("/", response_model=InstituteResponse)
def create_institute(
    data: InstituteCreate,
    db: Session = Depends(get_db),
    user=Depends(superadmin_only)
):
    exists = db.query(Institute).filter(Institute.code == data.code).first()
    if exists:
        raise HTTPException(status_code=400, detail="Institute code already exists")

    institute = Institute(
        name=data.name,
        code=data.code,
        address=data.address
    )

    db.add(institute)
    db.commit()
    db.refresh(institute)
    return institute


@router.get("/", response_model=list[InstituteResponse])
def list_institutes(
    db: Session = Depends(get_db),
    user=Depends(superadmin_only)
):
    return db.query(Institute).all()


@router.post("/{institute_id}/create-admin")
def create_admin_for_institute(
    institute_id: int,
    data: AdminCreate,
    db: Session = Depends(get_db),
    user=Depends(superadmin_only)
):
    institute = db.query(Institute).filter(Institute.id == institute_id).first()
    if not institute:
        raise HTTPException(status_code=404, detail="Institute not found")

    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    admin = User(
        name=data.name,
        email=data.email,
        password=hash_password(data.password),
        role="admin",
        institute_id=institute.id
    )

    db.add(admin)
    db.commit()

    return {
        "message": "Admin created successfully",
        "institute": institute.name,
        "admin_email": admin.email
    }

@router.get("/{institute_id}", response_model=InstituteResponse)
def get_institute(
    institute_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)   # admin allowed
):
    institute = db.query(Institute).filter(Institute.id == institute_id).first()
    if not institute:
        raise HTTPException(status_code=404, detail="Institute not found")
    return institute

@router.put("/{institute_id}", response_model=InstituteResponse)
def update_institute(
    institute_id: int,
    data: InstituteUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    # only admin of same institute OR superadmin
    if user.role not in ["admin", "superadmin"]:
        raise HTTPException(status_code=403)

    if user.role == "admin" and user.institute_id != institute_id:
        raise HTTPException(status_code=403)

    institute = db.query(Institute).filter(
        Institute.id == institute_id
    ).first()

    if not institute:
        raise HTTPException(status_code=404, detail="Institute not found")

    institute.name = data.name
    institute.target_line = data.target_line
    institute.phone = data.phone
    institute.website = data.website
    institute.address = data.address
    institute.country = data.country

    db.commit()
    db.refresh(institute)
    return institute
