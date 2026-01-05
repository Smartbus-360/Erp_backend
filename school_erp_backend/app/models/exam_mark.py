from sqlalchemy import Column, Integer, ForeignKey
from app.database import Base

class ExamMark(Base):
    __tablename__ = "exam_marks"

    id = Column(Integer, primary_key=True)

    exam_id = Column(Integer, ForeignKey("exams.id"))
    student_id = Column(Integer, nullable=False)
    subject_id = Column(Integer, nullable=False)

    marks = Column(Integer, nullable=False)
