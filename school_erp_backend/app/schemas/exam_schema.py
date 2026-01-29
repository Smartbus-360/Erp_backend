from typing import Optional
from pydantic import BaseModel
from datetime import date

class ExamCreate(BaseModel):
    name: str
    start_date: date
    end_date: date


class ExamResponse(BaseModel):
    id: int
    name: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    
    class Config:
        from_attributes = True


class ExamMarkCreate(BaseModel):
    exam_id: int
    student_id: int
    subject_id: int
    marks: int
