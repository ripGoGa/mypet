from datetime import date, datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class UploadedFile(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    original_name: str
    sha256: str = Field(unique=True)
    uploaded_at: datetime
    workouts: List['Workout'] = Relationship(back_populates='source_file')


class Workout(SQLModel, table=True):
    id: int = Field(primary_key=True, default=None)
    date: datetime
    duration_min: float
    distance_km: float
    avg_watts: Optional[float]
    normalized_power: Optional[float]
    intensity_factor: Optional[float]
    training_stress_score: Optional[float]
    avg_cadence: Optional[float]
    avg_speed: Optional[float]
    avg_heartrate: Optional[float]
    effort: Optional[float] = None
    ftp: Optional[float]

    source_file_id: Optional[int] = Field(default=None, foreign_key='uploadedfile.id')
    source_file: Optional[UploadedFile] = Relationship(back_populates='workouts')


class UserProfile(SQLModel, table=True):
    id: int = Field(primary_key=True, default=None)
    name: str
    birth_date: Optional[date]
    height_cm: Optional[int]
    weight_kg: Optional[float]
    ftp: Optional[float]
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
