from pydantic import BaseModel

class TimetableCreate(BaseModel):
    class_id: int
    section_id: int | None = None
    weekday_id: int
    period_no: int
    subject_id: int
    teacher_id: int


class TimetableResponse(BaseModel):
    id: int
    class_id: int
    section_id: int | None
    weekday_id: int
    period_no: int
    subject_id: int
    teacher_id: int

    class Config:
        from_attributes = True
