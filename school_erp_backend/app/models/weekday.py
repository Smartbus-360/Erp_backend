from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base



class Weekday(Base):
    __tablename__ = "weekdays"

    id = Column(Integer, primary_key=True)
    institute_id = Column(Integer, nullable=False)
    name = Column(String(20), nullable=False)
    is_active = Column(Boolean, default=True)
