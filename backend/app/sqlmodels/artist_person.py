from sqlmodel import SQLModel, Field, Relationship


class ArtistPerson(SQLModel, table=True):
    artist_id: int = Field(foreign_key="artist.id", primary_key=True)
    person_id: int = Field(foreign_key="person.id", primary_key=True)

    artist: "Artist" = Relationship(back_populates="artist_person_links")
    person: "Person" = Relationship(back_populates="artist_memberships")