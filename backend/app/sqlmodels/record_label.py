from typing import Optional
from sqlmodel import SQLModel, Field

class RecordLabel(SQLModel, table=True):
    __tablename__ = "record_label"
    id: int = Field(default=None, primary_key=True)
    name: str
    contact_email: Optional[str] = None