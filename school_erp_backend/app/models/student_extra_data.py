from sqlalchemy import Column, Integer, String
from app.database import Base

class StudentExtraData(Base):
    __tablename__ = "student_extra_data"

    id = Column(Integer, primary_key=True)

    student_id = Column(Integer, nullable=False)
    field_key = Column(String(50), nullable=False)

    value = Column(String(500), nullable=True)
