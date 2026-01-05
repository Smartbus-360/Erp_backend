from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base
from sqlalchemy.orm import relationship

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(150), nullable=False)
    designation = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)

    gender = Column(String(20), nullable=True)
    religion = Column(String(50), nullable=True)
    education = Column(String(100), nullable=True)
    address = Column(String(500), nullable=True)


    institute_id = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", backref="employee", uselist=False)
    