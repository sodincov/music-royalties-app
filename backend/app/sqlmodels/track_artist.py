from sqlmodel import SQLModel, Field

class TrackArtist(SQLModel, table=True):
    track_id: int = Field(foreign_key="track.id", primary_key=True)
    artist_id: int = Field(foreign_key="artist.id", primary_key=True)