from sqlalchemy import Column, Integer, String
from app.database import Base
from sqlalchemy import Enum

class FeeStructure(Base):
    __tablename__ = "fee_structures"

    id = Column(Integer, primary_key=True)
    class_id = Column(Integer, nullable=False)
    fee_name = Column(String(100))        # Tuition, Bus, Exam
    amount = Column(Integer, nullable=False)
    institute_id = Column(Integer, nullable=False)
    class_id = Column(Integer, nullable=True)
    section_id = Column(Integer, nullable=True)
    student_id = Column(Integer, nullable=True)
    # scope = Column(
    # Enum("ALL", "CLASS", "STUDENT", name="fee_scope"),
    # default="ALL",
    # nullable=False)
    scope = Column(String)  # ALL / CLASS / STUDENT

