from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse, UserResponse
from app.security import verify_password, create_access_token
from app.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.is_active:
        raise HTTPException(
        status_code=403,
        detail="Your account is disabled. Contact admin."
    )


    token = create_access_token({
        "user_id": user.id,
        "role": user.role,
        "institute_id": user.institute_id
    })

    return {
        "access_token": token,
        "role": user.role,
        "institute_id": user.institute_id
    }


@router.get("/me", response_model=UserResponse)
def me(user=Depends(get_current_user)):
    return user
