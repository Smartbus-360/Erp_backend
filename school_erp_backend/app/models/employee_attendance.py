from sqlalchemy import Column, Integer, Date, String
from app.database import Base

class EmployeeAttendance(Base):
    __tablename__ = "employee_attendance"

    id = Column(Integer, primary_key=True)

    employee_id = Column(Integer, nullable=False)
    institute_id = Column(Integer, nullable=False)

    date = Column(Date, nullable=False)
    status = Column(String(10))  # present | absent
