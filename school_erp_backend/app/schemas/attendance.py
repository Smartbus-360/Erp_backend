from pydantic import BaseModel
from datetime import date

class StudentAttendanceCreate(BaseModel):
    student_id: int
    class_id: int
    section_id: int | None = None
    date: date
    status: str  # present | absent


class EmployeeAttendanceCreate(BaseModel):
    employee_id: int
    date: date
    status: str
