from pydantic import BaseModel, EmailStr

class ManagerCreateRequest(BaseModel):
    email: EmailStr
    password: str
    nickname: str | None = None

class ManagerResponse(BaseModel):
    id: int
    email: str
    nickname: str | None
    role: str
    is_active: bool

    class Config:
        from_attributes = True

