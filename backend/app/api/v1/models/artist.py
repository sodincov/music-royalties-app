from pydantic import BaseModel
from typing import List, Optional

class ArtistCreateRequest(BaseModel):
    name: str
    member_ids: List[int]
    isni: Optional[str] = None

class ArtistUpdateRequest(BaseModel):
    name: Optional[str] = None
    member_ids: Optional[List[int]] = None
    isni: Optional[str] = None

class ArtistResponse(BaseModel):
    id: int
    name: str
    isni: Optional[str] = None
    is_approved: bool  # ← добавили!
    created_by_user_id: Optional[int] = None

    model_config = {"from_attributes": True}

class ArtistDetailResponse(BaseModel):
    id: int
    name: str
    isni: Optional[str] = None
    members: List["PersonResponse"] = []

    class Config:
        from_attributes = True

# Отложенные импорты + rebuild
from app.api.v1.models.person import PersonResponse

ArtistResponse.model_rebuild()
ArtistDetailResponse.model_rebuild()