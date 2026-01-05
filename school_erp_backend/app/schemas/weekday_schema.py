from pydantic import BaseModel

class WeekdayCreate(BaseModel):
    name: str
