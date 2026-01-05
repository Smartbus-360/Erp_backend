from sqlalchemy import Column, Integer, Boolean, ForeignKey
from app.database import Base

class EmployeePermission(Base):
    __tablename__ = "employee_permissions"

    id = Column(Integer, primary_key=True)

    employee_id = Column(Integer, ForeignKey("employees.id"), unique=True)

    can_students = Column(Boolean, default=False)
    can_attendance = Column(Boolean, default=False)
    can_exams = Column(Boolean, default=False)
    can_fees = Column(Boolean, default=False)
    can_salary = Column(Boolean, default=False)
    can_homework = Column(Boolean, default=False)
