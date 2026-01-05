from pydantic import BaseModel
from datetime import date
class ExamScheduleItem(BaseModel):
    exam_date: date
    subject_id: int
    teacher_id: int

class ExamScheduleCreate(BaseModel):
    class_id: int
    section_id: int
    schedules: list[ExamScheduleItem]
