from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from app.database import Base
from datetime import datetime


class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)      # Unit Test, Mid Term
    institute_id = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
