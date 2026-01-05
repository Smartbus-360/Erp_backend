from sqlalchemy import Column, Integer, String
from app.database import Base

class Period(Base):
    __tablename__ = "periods"

    id = Column(Integer, primary_key=True)
    institute_id = Column(Integer, nullable=False)

    name = Column(String(50))        # Period 1, First Period
    start_time = Column(String(10))  # 09:00
    end_time = Column(String(10))    # 09:45
    order_no = Column(Integer)
