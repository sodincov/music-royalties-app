from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship

from .artist_person import ArtistPerson
from .album_artist import AlbumArtist
from .track_artist import TrackArtist

class Artist(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    isni: Optional[str] = Field(unique=True)
    marketing_expenses: Optional[float] = None
    advance_expenses: Optional[float] = None

    # === НОВЫЕ ПОЛЯ ===
    is_approved: bool = Field(default=False)
    created_by_user_id: Optional[int] = None

    artist_person_links: List["ArtistPerson"] = Relationship(back_populates="artist")
    members: List["Person"] = Relationship(link_model=ArtistPerson)

    albums: List["Album"] = Relationship(back_populates="artists", link_model=AlbumArtist)
    tracks: List["Track"] = Relationship(back_populates="artists", link_model=TrackArtist)

    def __repr__(self):
        return f"<Artist {self.name}>"