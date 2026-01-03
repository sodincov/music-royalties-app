# app/api/v1/models/track.py

from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import date # Или используйте str, если период приходит строком

from .album import Album
from .artist import Artist
from .track_artist import TrackArtist
from .track_person_share import TrackPersonShare
from .record_label import RecordLabel
# УБРАТЬ ИМПОРТ: from .usage_report import UsageReport

class Track(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    isrc: str  # ← убираем unique из модели (будем проверять вручную)
    genre: Optional[str] = None

    label_id: Optional[int] = Field(default=None, foreign_key="record_label.id")
    label: "RecordLabel" = Relationship()
    label_share_percentage: float = Field(ge=0.0, le=100.0, default=20.0)

    scope_of_copyright: Optional[float] = None
    scope_of_related_rights: Optional[float] = None
    neighboring_rights_share: Optional[float] = None
    label_rights_share: Optional[float] = None
    label_monetization_share: Optional[float] = None

    marketing_expenses: Optional[float] = None
    advance_expenses: Optional[float] = None

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

    album_id: int = Field(foreign_key="album.id")
    album: Album = Relationship(back_populates="tracks")

    artists: List[Artist] = Relationship(back_populates="tracks", link_model=TrackArtist)
    track_person_shares: List[TrackPersonShare] = Relationship(back_populates="track")
    usage_reports: List["UsageReport"] = Relationship(back_populates="track")

    # === НОВЫЕ ПОЛЯ СОГЛАСОВАНИЯ ===
    is_approved: bool = Field(default=False)
    created_by_user_id: Optional[int] = None

    def __repr__(self):
        return f"<Track {self.title} (ISRC: {self.isrc})>"
