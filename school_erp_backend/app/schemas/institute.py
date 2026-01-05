from pydantic import BaseModel
from typing import Optional

class InstituteCreate(BaseModel):
    name: str
    code: str
    address: str | None = None


class InstituteResponse(BaseModel):
    id: int
    name: str
    code: str
    address: str | None
    target_line: str | None = None
    phone: str | None = None
    website: str | None = None
    country: str | None = None

    class Config:
        from_attributes = True


class AdminCreate(BaseModel):
    name: str
    email: str
    password: str

class InstituteUpdate(BaseModel):
    name: str
    target_line: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    country: Optional[str] = None
