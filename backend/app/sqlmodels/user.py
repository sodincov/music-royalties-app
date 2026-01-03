from typing import Optional
from sqlmodel import SQLModel, Field
from enum import Enum

class Role(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    nickname: Optional[str] = Field(default=None)
    is_active: bool = True
    role: Role = Field(default=Role.MANAGER)

