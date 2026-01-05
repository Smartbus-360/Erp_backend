from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base


class EmployeeExtraData(Base):
    __tablename__ = "employee_extra_data"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, nullable=False)
    field_key = Column(String(50), nullable=False)
    value = Column(String(255), nullable=True)
