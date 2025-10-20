from datetime import date, datetime, timedelta
from pathlib import Path
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
    duration: timedelta
    moving_time: timedelta
    distance_km: float
    avg_watts: Optional[int]
    normalized_power: Optional[float]
    intensity_factor: Optional[float]
    training_stress_score: Optional[float]
    avg_cadence: Optional[int]
    avg_speed: Optional[float]
    avg_speed_without_stop: Optional[int]
    avg_heartrate: Optional[int]
    max_heartrate: Optional[float]
    calories_burned: Optional[int]

    source_file_id: Optional[int] = Field(default=None, foreign_key='uploadedfile.id')
    source_file: Optional['UploadedFile'] = Relationship(back_populates='workouts')


class UserProfile(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    name: str
    birth_date: Optional[date]
    height_cm: Optional[int]
    weight_kg: float
    ftp: int
    updated_at: datetime = Field(default_factory=datetime.now)
