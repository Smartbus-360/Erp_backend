from pydantic import BaseModel
from typing import List, Optional


class SubjectCreate(BaseModel):
    name: str


class AssignSubject(BaseModel):
    class_id: int
    section_id: int | None = None
    subject_ids: list[int]
    teacher_id: int | None = None


class SubjectResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class SubjectTeacherItem(BaseModel):
    subject_id: int
    teacher_id: Optional[int]

class SubjectAssignRequest(BaseModel):
    class_id: int
    subjects: List[SubjectTeacherItem]
