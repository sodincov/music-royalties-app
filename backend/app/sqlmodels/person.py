from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship

class Person(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    last_name: str
    first_name: str
    middle_name: Optional[str] = None
    email: str = Field(unique=True)
    phone: Optional[str] = None
    marketing_expenses: Optional[float] = None
    advance_expenses: Optional[float] = None

    is_approved: bool = Field(default=False)
    created_by_user_id: Optional[int] = None

    artist_memberships: List["ArtistPerson"] = Relationship(back_populates="person")
    track_person_shares: List["TrackPersonShare"] = Relationship(back_populates="person")

    def __repr__(self):
        return f"<Person {self.first_name} {self.last_name}>"