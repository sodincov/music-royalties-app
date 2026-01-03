from pydantic import BaseModel


class TrackPersonShareResponse(BaseModel):
    person_id: int
    share_percentage: float

    class Config:
        from_attributes = True