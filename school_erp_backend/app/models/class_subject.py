from sqlalchemy import Column, Integer, ForeignKey
from app.database import Base

class ClassSubject(Base):
    __tablename__ = "class_subjects"

    id = Column(Integer, primary_key=True)
    class_id = Column(Integer, ForeignKey("classes.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    teacher_id = Column(Integer, nullable=True)
    institute_id = Column(Integer, nullable=False)
