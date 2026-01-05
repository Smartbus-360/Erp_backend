from pydantic import BaseModel
from datetime import date

class StudentAttendanceReportItem(BaseModel):
    student_id: int
    student_name: str
    class_name: str
    section: str | None
    date: date
    status: str

class EmployeeAttendanceReportItem(BaseModel):
    employee_id: int
    employee_name: str
    date: date
    status: str
