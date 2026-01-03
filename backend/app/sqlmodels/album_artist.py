from sqlmodel import SQLModel, Field

class AlbumArtist(SQLModel, table=True):
    __tablename__ = "album_artist"
    album_id: int = Field(foreign_key="album.id", primary_key=True)
    artist_id: int = Field(foreign_key="artist.id", primary_key=True)

