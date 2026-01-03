from sqlmodel import SQLModel, Field, Relationship


class TrackPersonShare(SQLModel, table=True):
    __tablename__ = "track_person_share"

    track_id: int = Field(foreign_key="track.id", primary_key=True)
    person_id: int = Field(foreign_key="person.id", primary_key=True)

    share_of_monetization_of_copyrights: float = Field(default=0.0, ge=0.0, le=100.0, description="Доля лицензиата в авторских правах трека")
    share_of_monetization_of_related_rights: float = Field(default=0.0, ge=0.0, le=100.0, description="Доля лицензиата в смежных правах трека")

    copyrights: float = Field(default=0.0, ge=0.0, le=100.0, description="Доля лицензиара по авторским правам (от доли лицензиата)")
    related_rights: float = Field(default=0.0, ge=0.0, le=100.0, description="Доля лицензиара по смежным правам (от доли лицензиата)")

    # Связи
    track: "Track" = Relationship(back_populates="track_person_shares")
    person: "Person" = Relationship(back_populates="track_person_shares")

    def __repr__(self):
        return (
            f"<TrackPersonShare "
            f"track_id={self.track_id}, person_id={self.person_id}, "
            f"share_of_monetization_of_copyrights={self.share_of_monetization_of_copyrights}%, "
            f"share_of_monetization_of_related_rights={self.share_of_monetization_of_related_rights}%, "
            f"copyrights={self.copyrights}%, "
            f"related_rights={self.related_rights}%"
            ">"
        )