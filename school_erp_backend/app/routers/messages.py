from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional

from app.database import get_db
from app.auth import get_current_user
from app.models.message import Message, MessageAttachment
from app.schemas.MessageResponse import MessageResponse
from app.utils.file_upload import save_message_file

router = APIRouter(prefix="/messages", tags=["Messaging"])


# ===================== SEND MESSAGE =====================
@router.post("/send", response_model=MessageResponse)
def send_message(
    send_type: str = Form(...),      # student / employee / institute
    message: str = Form(...),
    receiver_id: Optional[int] = Form(None),
    category: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    sender_role = current_user.role
    print("DEBUG send_type =", send_type)
    print("DEBUG all form data received")

    # -------- MAP send_type → receiver_role --------
    if send_type not in ["student", "employee", "institute"]:
        raise HTTPException(400, "Invalid send type")

    receiver_role = send_type

    # -------- ROLE RULES --------
    if sender_role == "admin":
        pass  # admin can message anyone
    elif sender_role == "employee":
        if receiver_role != "student":
            raise HTTPException(403, "Employees can message students only")
    elif sender_role == "student":
        if receiver_role != "employee":
            raise HTTPException(403, "Students can message employees only")
        if category != "teacher":
            raise HTTPException(403, "Students can message teachers only")
    else:
        raise HTTPException(403, "Invalid sender role")

    # -------- CREATE MESSAGE --------
    new_message = Message(
        sender_id=current_user.id,
        sender_role=sender_role,
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
