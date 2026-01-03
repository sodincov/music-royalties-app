from typing import List, Optional
from pydantic import BaseModel
from app.api.v1.models.artist import ArtistResponse

class TrackPersonShareResponse(BaseModel):
    person_id: int
    share_author: float
    share_neighboring: float

class AuthorRightRequest(BaseModel):
    person_id: int
    share: float  # <-- Это будет share_author
    licensor_share: float # <-- Это будет licensor_share_author

class NeighboringRightRequest(BaseModel):
    person_id: int
    share: float  # <-- Это будет share_neighboring
    licensor_share: float # <-- Это будет licensor_share_neighboring

class TrackCreateRequest(BaseModel):
    title: str
    album_id: int
    isrc: Optional[str] = None
    genre: Optional[str] = None
    artist_ids: List[int]
    music_authors: Optional[str] = None
    lyrics_authors: Optional[str] = None
    scope_of_copyright: Optional[float] = None
    scope_of_related_rights: Optional[float] = None
    neighboring_rights_share: Optional[float] = None
    label_rights_share: Optional[float] = None
    label_monetization_share: Optional[float] = None
    artist_monetization_shares: Optional[str] = None
    marketing_expenses: Optional[float] = None
    advance_expenses: Optional[float] = None
    advance: Optional[str] = None
    marketing: Optional[str] = None
    text: Optional[str] = None
    karaoke: Optional[str] = None
    synclab: Optional[str] = None
    copyright: Optional[str] = None
    related_rights: Optional[str] = None
    is_ringtone_added: bool = False
    has_video_clip: bool = False
    is_lyrics_added: bool = False
    is_karaoke_sync_added: bool = False

    artist_ids: List[int]
    author_rights: Optional[List[AuthorRightRequest]] = []  # <-- Убедитесь, что это модель
    neighboring_rights: Optional[List[NeighboringRightRequest]] = []


    class Config:
        from_attributes = True

class TrackUpdateRequest(BaseModel):
    title: Optional[str] = None
    isrc: Optional[str] = None
    genre: Optional[str] = None
    album_id: Optional[int] = None
    artist_ids: Optional[List[int]] = None
    music_authors: Optional[str] = None
    lyrics_authors: Optional[str] = None
    scope_of_copyright: Optional[float] = None
    scope_of_related_rights: Optional[float] = None
    neighboring_rights_share: Optional[float] = None
    label_rights_share: Optional[float] = None
    label_monetization_share: Optional[float] = None
    artist_monetization_shares: Optional[str] = None
    marketing_expenses: Optional[float] = None
    advance_expenses: Optional[float] = None
    advance: Optional[str] = None
    marketing: Optional[str] = None
    text: Optional[str] = None
    karaoke: Optional[str] = None
    synclab: Optional[str] = None
    copyright: Optional[str] = None
    related_rights: Optional[str] = None
    is_ringtone_added: Optional[bool] = None
    has_video_clip: Optional[bool] = None
    is_lyrics_added: Optional[bool] = None
    is_karaoke_sync_added: Optional[bool] = None
    person_shares: Optional[List[dict]] = None

class TrackResponse(BaseModel):
    id: int
    title: str
    isrc: Optional[str] = None
    genre: Optional[str] = None
    label_id: Optional[int] = None
    label_share_percentage: Optional[float] = None
    scope_of_copyright: Optional[float] = None
    scope_of_related_rights: Optional[float] = None
    neighboring_rights_share: Optional[float] = None
    label_rights_share: Optional[float] = None
    label_monetization_share: Optional[float] = None
    marketing_expenses: Optional[float] = None
    advance_expenses: Optional[float] = None
    is_approved: bool  # ← ДОБАВЬ ЭТУ СТРОКУ
    created_by_user_id: Optional[int] = None
    is_ringtone_added: bool = False
    has_video_clip: bool = False
    is_lyrics_added: bool = False
    is_karaoke_sync_added: bool = False
    text: Optional[str] = None
    karaoke: Optional[str] = None
    synclab: Optional[str] = None
    copyright: Optional[str] = None
    related_rights: Optional[str] = None
    advance: Optional[str] = None
    marketing: Optional[str] = None
    album_id: int
    album_title: Optional[str] = None  # ← можно оставить
    artists: List["ArtistResponse"]
    artist_ids: List[int]

    model_config = {"from_attributes": True}



TrackResponse.model_rebuild()
class TrackDetailResponse(BaseModel):
    id: int
    title: str
    isrc: Optional[str] = None
    genre: Optional[str] = None
    music_authors: Optional[str] = None
    lyrics_authors: Optional[str] = None
    scope_of_copyright: Optional[float] = None
    scope_of_related_rights: Optional[float] = None
    neighboring_rights_share: Optional[float] = None
    label_rights_share: Optional[float] = None
    label_monetization_share: Optional[float] = None
    artist_monetization_shares: Optional[str] = None
    marketing_expenses: Optional[float] = None
    advance_expenses: Optional[float] = None
    advance: Optional[str] = None
    marketing: Optional[str] = None
    text: Optional[str] = None
    karaoke: Optional[str] = None
    synclab: Optional[str] = None
    copyright: Optional[str] = None
    related_rights: Optional[str] = None
    is_ringtone_added: bool
    has_video_clip: bool
    is_lyrics_added: bool
    is_karaoke_sync_added: bool
    album_id: int
    artists: List["ArtistDetailResponse"] = []
    track_person_shares: List[TrackPersonShareResponse] = []
    author_rights: Optional[List[AuthorRightRequest]] = []  # <-- Обновлено
    neighboring_rights: Optional[List[NeighboringRightRequest]] = []

    class Config:
        from_attributes = True

class TrackPersonShareDetailResponse(BaseModel):
    person_id: int
    share_percentage: float

    class Config:
        from_attributes = True



# Отложенные импорты
from app.api.v1.models.artist import ArtistResponse, ArtistDetailResponse

TrackResponse.model_rebuild()
TrackDetailResponse.model_rebuild()
TrackPersonShareDetailResponse.model_rebuild()