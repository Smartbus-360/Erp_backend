from pydantic import BaseModel

class SubjectResult(BaseModel):
    subject_name: str
    marks: int


class ResultCard(BaseModel):
    student_id: int
    student_name: str
    class_name: str
    exam_name: str

    subjects: list[SubjectResult]

    total_marks: int
    percentage: float
    result: str  # PASS / FAIL
