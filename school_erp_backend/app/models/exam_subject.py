from sqlalchemy import Column, Integer, ForeignKey
from app.database import Base

class ExamSubject(Base):
    __tablename__ = "exam_subjects"

    id = Column(Integer, primary_key=True)
    exam_id = Column(Integer, ForeignKey("exams.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
