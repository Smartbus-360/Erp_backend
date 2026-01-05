from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    institute_id: int | None


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    institute_id: int | None

    class Config:
        from_attributes = True
