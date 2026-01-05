from sqlalchemy import Column, Integer, String,ForeignKey
from app.database import Base
from sqlalchemy.orm import relationship

class SchoolClass(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)   # e.g. "10", "LKG"
    institute_id = Column(Integer, nullable=False)
    sections = relationship("Section", back_populates="school_class")
    class_teacher_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    teacher = relationship("Employee")
    sections = relationship("Section", back_populates="school_class")
