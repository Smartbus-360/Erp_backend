from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class Timetable(Base):
    __tablename__ = "timetables"

    id = Column(Integer, primary_key=True)
    institute_id = Column(Integer, nullable=False)

    class_id = Column(Integer, nullable=False)
    section_id = Column(Integer, nullable=True)
    weekday_id = Column(Integer, nullable=False)

    subject_id = Column(Integer, nullable=False)
    teacher_id = Column(Integer, nullable=False)
    period_no = Column(Integer, nullable=False)
