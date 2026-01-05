from pydantic import BaseModel

class SyllabusCreate(BaseModel):
    class_id: int
    section_id: int | None = None
    subject_id: int
    subject_name: str
    teacher_id: int
    title: str | None=None
    description: str | None = None


class SyllabusResponse(SyllabusCreate):
    id: int

    class Config:
        from_attributes = True
