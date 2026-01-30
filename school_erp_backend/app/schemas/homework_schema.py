from pydantic import BaseModel
from datetime import date
from typing import Optional


class HomeworkCreate(BaseModel):
    class_id: int
    section_id: Optional[int] = None
    subject_id: int
    teacher_id: Optional[int] = None
    title: str
    description: str
    due_date: date


class HomeworkResponse(BaseModel):
    id: int
    class_id: int
    section_id: Optional[int]
    subject_id: int
    teacher_id: Optional[int]

    title: str
    description: str
    due_date: date

    # Derived / joined fields
    teacher_name: Optional[str] = None
    class_name: Optional[str] = None
    subject_name: Optional[str] = None

    class Config:
        from_attributes = True
