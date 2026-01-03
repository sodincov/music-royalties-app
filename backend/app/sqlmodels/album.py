from typing import List, Optional
from datetime import date
from sqlmodel import SQLModel, Field, Relationship

from .album_artist import AlbumArtist


class Album(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    type: str
    release_date: Optional[date] = None
    upc: Optional[str] = None  # ← убираем unique=True (см. примечание)
    marketing_expenses: Optional[float] = None
    advance_expenses: Optional[float] = None
    aggregator: Optional[str] = None
    yoga: Optional[str] = None
    Zaycev: Optional[str] = None
    additional_sites: Optional[str] = None

    version: Optional[str] = None
    subgenre: Optional[str] = None
    isrc: Optional[str] = None  # ← убираем unique=True
    zaycev_star: Optional[str] = None
    synclab_star: Optional[str] = None

    # === НОВЫЕ ПОЛЯ СОГЛАСОВАНИЯ ===
    is_approved: bool = Field(default=False)
    created_by_user_id: Optional[int] = None

    artists: List["Artist"] = Relationship(back_populates="albums", link_model=AlbumArtist)
    tracks: List["Track"] = Relationship(back_populates="album")

    def __repr__(self):
        return f"<Album {self.title}>"