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
from app.models.section import Section
from app.models.student import Student
from app.models.employee import Employee
from app.models.user import User

router = APIRouter(prefix="/messages", tags=["Messaging"])


def get_class_coordinator(db: Session, class_id: int):
    cls = (
        db.query(SchoolClass)
        .filter(SchoolClass.id == class_id)
        .first()
    )

    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")

    if not cls.class_coordinator_id:
        raise HTTPException(
            status_code=400,
            detail="Class coordinator not assigned"
        )

    return cls.class_coordinator_id


def get_section_teacher(db: Session, class_id: int, section_name: str):
    sec = db.query(Section).filter(
        Section.class_id == class_id,
        Section.name == section_name
    ).first()

    if not sec or not sec.teacher_id:
        raise HTTPException(400, "Teacher not assigned for this section")

    return sec.teacher_id

def get_students_by_class(db, class_id, institute_id):
    return db.query(Student).filter(
        Student.class_id == class_id,
        Student.institute_id == institute_id
    ).all()


def get_student_by_admission(db, admission_no, institute_id):
    student = db.query(Student).filter(
        Student.admission_no == admission_no,
        Student.institute_id == institute_id
    ).first()

    if not student:
        raise HTTPException(404, "Student not found")

    return student.user_id


def get_all_students(institute_id):
    return {
        "receiver_role": "student",
        "receiver_id": None
    }


def get_employees_by_role(db, role, institute_id):
    employees = db.query(Employee).filter(
        Employee.role == role,
        Employee.institute_id == institute_id
    ).all()

    if not employees:
        raise HTTPException(404, "No employees found")

    return employees


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

    # if send_scope == "class":
    #     receiver_id = get_class_coordinator(db, class_id)
    #     receiver_role = "employee"

    # elif send_scope == "class_section":
    #     if not section:
    #         raise HTTPException(400, "Section is required")
    #     receiver_id = get_section_teacher(db, class_id, section)
    #     receiver_role = "employee"

    # else:
    #     raise HTTPException(400, "Invalid send_scope")
    receiver_role = None
    receiver_id = None

    if send_scope == "class":
        receiver_id = get_class_coordinator(db, class_id)
        receiver_role = "employee"

    elif send_scope == "class_section":
        receiver_id = get_section_teacher(db, class_id, section)
        receiver_role = "employee"

    elif send_scope == "class_students":
        receiver_role = "student"
        receiver_id = None
        category = f"class:{class_id}"

    elif send_scope == "student_admission":
        admission_no = Form(...)
        receiver_id = get_student_by_admission(
            db, admission_no, current_user.institute_id
        )
        receiver_role = "student"

    elif send_scope == "all_students":
        receiver_role = "student"
        receiver_id = None
        category = "all_students"

    elif send_scope == "employees_by_role":
        role = Form(...)
        receiver_role = "employee"
        receiver_id = None
        category = role

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
