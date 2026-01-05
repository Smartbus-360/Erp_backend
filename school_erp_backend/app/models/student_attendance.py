from sqlalchemy import Column, Integer, Date, String
from app.database import Base

class StudentAttendance(Base):
    __tablename__ = "student_attendance"

    id = Column(Integer, primary_key=True)

    class_id = Column(Integer, nullable=False)
    section_id = Column(Integer, nullable=False)

    student_id = Column(Integer, nullable=False)
    institute_id = Column(Integer, nullable=False)

    date = Column(Date, nullable=False)
    status = Column(String(10))  # present | absent
