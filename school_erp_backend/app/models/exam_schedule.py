from sqlalchemy import Column, Integer, String, Date,ForeignKey
from app.database import Base

class ExamSchedule(Base):
    __tablename__ = "exam_schedules"

    id = Column(Integer, primary_key=True)

    exam_id = Column(Integer, ForeignKey("exams.id"))
    class_id = Column(Integer, ForeignKey("classes.id"))
    section_id = Column(Integer, ForeignKey("sections.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    teacher_id = Column(Integer, ForeignKey("employees.id"))

    exam_date = Column(Date, nullable=False)

    institute_id = Column(Integer, nullable=False)
