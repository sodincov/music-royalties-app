from typing import Optional
from pydantic import BaseModel, EmailStr

class PersonCreateRequest(BaseModel):
    last_name: str
    first_name: str
    middle_name: Optional[str] = None
    email: str
    phone: Optional[str] = None

class PersonUpdateRequest(BaseModel):
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

class PersonResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    email: str
    phone: Optional[str] = None
    is_approved: bool
    created_by_user_id: Optional[int] = None  # ← теперь может быть None

    model_config = {"from_attributes": True}

PersonResponse.model_rebuild()