from pydantic import BaseModel
from datetime import date

class ExamCreate(BaseModel):
    name: str
    # class_id: int
    start_date: date
    end_date: date
    # subject_ids: list[int]


class ExamResponse(BaseModel):
    id: int
    name: str
    class_id: int

    class Config:
        from_attributes = True


class ExamMarkCreate(BaseModel):
    exam_id: int
    student_id: int
    subject_id: int
    marks: int
