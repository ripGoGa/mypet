from datetime import date, datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class UploadedFile(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    original_name: str
    sha256: str = Field(unique=True)
    uploaded_at: datetime


class Workout(SQLModel, table=True):
    id: int = Field(primary_key=True, default=None)
    date: date
    sport: str = Field(default='cycling')
    duration_min: float
    distance_km: float
    effort: Optional[float] = None
    source_file_id: Optional[int] = Field(default=None, foreign_key='uploadedfile.id')
