from pydantic import BaseModel
from datetime import date
from typing import List, Optional

class HomeworkCreate(BaseModel):
    class_id: int
    # section: str | None = None
section_id: Optional[int] = None
subject_id: int
    teacher_id: Optional[int] = None   
    title: str
    description: str
    due_date: date


class HomeworkResponse(BaseModel):
    id: int
    class_id: int
    section: str | None
    subject_id: int
    teacher_id: int | None

    title: str
    description: str
    due_date: date

    # 👇 Derived fields (NOT in DB)
    teacher_name: str | None = None
    class_name: str | None = None
    subject_name: str | None = None

    class Config:
        from_attributes = True
