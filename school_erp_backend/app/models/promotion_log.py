from sqlalchemy import Column, Integer, String, Date
from datetime import date
from app.database import Base

class PromotionLog(Base):
    __tablename__ = "promotion_logs"

    id = Column(Integer, primary_key=True)

    student_id = Column(Integer, nullable=False)
    from_class = Column(String(50))
    to_class = Column(String(50))


    from_section = Column(String(10))
    to_section = Column(String(10))

    promoted_on = Column(Date, default=date.today)

    institute_id = Column(Integer, nullable=False)
