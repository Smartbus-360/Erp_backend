from sqlalchemy import Column, Integer, String, Date
from app.database import Base

class Homework(Base):
    __tablename__ = "homework"

    id = Column(Integer, primary_key=True)

    class_id = Column(Integer, nullable=False)
    section = Column(String(10), nullable=True)
    subject_id = Column(Integer, nullable=False)
    teacher_id = Column(Integer, nullable=True)

    title = Column(String(200), nullable=False)
    description = Column(String(1000), nullable=False)

    due_date = Column(Date, nullable=False)

    institute_id = Column(Integer, nullable=False)
