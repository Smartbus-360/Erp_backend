from pydantic import BaseModel

class PeriodCreate(BaseModel):
    name: str
    start_time: str
    end_time: str
    order_no: int


class PeriodResponse(PeriodCreate):
    id: int

    class Config:
        from_attributes = True
