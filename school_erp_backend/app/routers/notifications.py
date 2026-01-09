from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models.message import Message

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/unread")
def unread_notifications(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return db.query(Message).filter(
        Message.receiver_role == current_user.role,
        Message.institute_id == current_user.institute_id,
        Message.is_read == False
    ).order_by(Message.created_at.desc()).limit(10).all()
