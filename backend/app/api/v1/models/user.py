from pydantic import BaseModel, EmailStr
from typing import Optional

from app.sqlmodels.user import Role


class ManagerCreateRequest(BaseModel):
    email: EmailStr
    password: str
    nickname: Optional[str] = None

class ManagerCreateResponse(BaseModel):
    id: int
    email: EmailStr
    nickname: Optional[str]
    role: Role

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: int
    email: str
    role: Role
    is_active: bool

    class Config:
        from_attributes = True