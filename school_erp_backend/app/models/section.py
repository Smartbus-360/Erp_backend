from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base
from sqlalchemy.orm import relationship

class Section(Base):
    __tablename__ = "sections"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(10), nullable=False)   # A, B, C
    class_id = Column(Integer, ForeignKey("classes.id"))
    teacher_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    teacher = relationship("Employee")
    institute_id = Column(Integer, nullable=False)
    school_class = relationship("SchoolClass", back_populates="sections")
