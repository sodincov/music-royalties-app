from typing import List, Optional
from datetime import date
from pydantic import BaseModel

class AlbumCreateRequest(BaseModel):
    title: str
    type: str
    release_date: Optional[date] = None
    upc: Optional[str] = None
    artist_ids: List[int]
    marketing_budget: Optional[float] = None
    advance: Optional[float] = None
    aggregator: Optional[str] = None
    yoga: Optional[str] = None
    additional_sites: Optional[str] = None
    # === НОВЫЕ ПОЛЯ ===
    version: Optional[str] = None
    subgenre: Optional[str] = None
    isrc: Optional[str] = None
    zaycev_star: Optional[str] = None
    synclab_star: Optional[str] = None

class AlbumUpdateRequest(BaseModel):
    title: Optional[str] = None
    type: Optional[str] = None
    release_date: Optional[date] = None
    upc: Optional[str] = None
    artist_ids: Optional[List[int]] = None
    marketing_budget: Optional[float] = None
    advance: Optional[float] = None
    aggregator: Optional[str] = None
    yoga: Optional[str] = None
    additional_sites: Optional[str] = None
    # === НОВЫЕ ПОЛЯ ===
    version: Optional[str] = None
    subgenre: Optional[str] = None
    isrc: Optional[str] = None
    zaycev_star: Optional[str] = None
    synclab_star: Optional[str] = None

class AlbumResponse(BaseModel):
    id: int
    title: str
    type: str
    release_date: Optional[date] = None
    upc: Optional[str] = None
    is_approved: bool
    created_by_user_id: Optional[int] = None
    marketing_budget: Optional[float] = None
    advance: Optional[float] = None
    aggregator: Optional[str] = None
    yoga: Optional[str] = None
    additional_sites: Optional[str] = None
    # === НОВЫЕ ПОЛЯ ===
    version: Optional[str] = None
    subgenre: Optional[str] = None
    isrc: Optional[str] = None
    zaycev_star: Optional[str] = None
    synclab_star: Optional[str] = None

    class Config:
        from_attributes = True

class AlbumDetailResponse(BaseModel):
    id: int
    title: str
    type: str
    release_date: Optional[date] = None
    upc: Optional[str] = None
    is_approved: bool  # ← ДОБАВЬ ЭТУ СТРОКУ
    artists: List["ArtistResponse"] = []
    tracks: List["TrackResponse"] = []
    version: Optional[str] = None
    subgenre: Optional[str] = None
    isrc: Optional[str] = None
    zaycev_star: Optional[str] = None
    synclab_star: Optional[str] = None

    model_config = {"from_attributes": True}

# Отложенные импорты
from app.api.v1.models.artist import ArtistResponse
from app.api.v1.models.track import TrackResponse

AlbumResponse.model_rebuild()
AlbumDetailResponse.model_rebuild()