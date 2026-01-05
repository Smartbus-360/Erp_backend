from pydantic import BaseModel

class SubjectCreate(BaseModel):
    name: str


class AssignSubject(BaseModel):
    class_id: int
    section_id: int | None = None
    subject_ids: list[int]


class SubjectResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
