from sqlalchemy import Column, Integer, String, Text
from app.database import Base

class Syllabus(Base):
    __tablename__ = "syllabus"

    id = Column(Integer, primary_key=True)

    institute_id = Column(Integer, nullable=False)

    class_id = Column(Integer, nullable=False)
    section_id = Column(Integer, nullable=True)

    subject_id = Column(Integer, nullable=False)
    teacher_id = Column(Integer, nullable=False)

    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
