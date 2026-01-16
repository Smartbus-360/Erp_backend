from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional

from app.database import get_db
from app.auth import get_current_user
from app.models.message import Message, MessageAttachment
from app.schemas.MessageResponse import MessageResponse
from app.utils.file_upload import save_message_file
from app.models.class_model import SchoolClass
from app.models.class_subject import ClassSubject

router = APIRouter(prefix="/messages", tags=["Messaging"])


def get_class_coordinator(db, class_id):
    cls = db.query(Class).filter(Class.id == class_id).first()
    if not cls or not cls.class_coordinator_id:
        raise HTTPException(400, "Class coordinator not assigned")
    return cls.class_coordinator_id

def get_section_teacher(db, class_id, section):
    subject = db.query(ClassSubject).filter(
        ClassSubject.class_id == class_id,
        ClassSubject.section == section
    ).first()

    if not subject or not subject.teacher_id:
        raise HTTPException(400, "Teacher not assigned for this section")

    return subject.teacher_id

# ===================== SEND MESSAGE =====================
@router.post("/send", response_model=MessageResponse)
def send_message(
    send_scope: str = Form(...),     # "class" or "class_section"
    class_id: int = Form(...),
    section: Optional[str] = Form(None),
    message: str = Form(...),
    category: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    sender_role = current_user.role
    # -------- ROLE RESTRICTION --------
    if sender_role not in ["admin", "employee"]:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to send class-based messages"
        )

    if send_scope == "class":
        receiver_id = get_class_coordinator(db, class_id)
        receiver_role = "employee"

    elif send_scope == "class_section":
        if not section:
            raise HTTPException(400, "Section is required")
        receiver_id = get_section_teacher(db, class_id, section)
        receiver_role = "employee"

    else:
        raise HTTPException(400, "Invalid send_scope")

    # -------- CREATE MESSAGE --------
    new_message = Message(
        sender_id=current_user.id,
        sender_role=current_user.role,
        receiver_role=receiver_role,
        receiver_id=receiver_id,      # None = broadcast
        category=category,
        title=title,
        message=message,
        institute_id=current_user.institute_id
    )

    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    # -------- ATTACHMENTS --------
    if files:
        for file in files:
            if not file.filename:
                continue
            saved = save_message_file(file)
            attachment = MessageAttachment(
                message_id=new_message.id,
                file_name=saved["file_name"],
                file_path=saved["file_path"],
                file_type=saved["file_type"]
            )
            db.add(attachment)
        db.commit()

    return new_message


# ===================== INBOX =====================
@router.get("/inbox", response_model=List[MessageResponse])
def inbox(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    q = db.query(Message).filter(
        Message.institute_id == current_user.institute_id,
        Message.receiver_role == current_user.role,
        or_(
            Message.receiver_id == None,
            Message.receiver_id == current_user.id
        )
    )

    # category-based delivery (teachers)
    if current_user.role == "employee":
        q = q.filter(
            or_(
                Message.category == None,
                Message.category == current_user.designation
            )
        )

    return q.order_by(Message.created_at.desc()).all()


# ===================== MARK READ =====================
@router.patch("/{message_id}/read")
def mark_read(
    message_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    msg = db.query(Message).filter(
        Message.id == message_id,
        Message.institute_id == current_user.institute_id
    ).first()

    if not msg:
        raise HTTPException(404, "Message not found")

    msg.is_read = True
    db.commit()

    return {"status": "read"}
