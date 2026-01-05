from pydantic import BaseModel

class PromoteStudent(BaseModel):
    student_ids: list[int]
    to_class_id: int
    to_section: str | None = None
