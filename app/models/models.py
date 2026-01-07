from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional, List, Text
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
    avg_heartrate: Optional[int] = None
    max_heartrate: Optional[float] = None
    calories_burned: Optional[int]

    source_file_id: Optional[int] = Field(default=None, foreign_key='uploadedfile.id')
    source_file: Optional['UploadedFile'] = Relationship(back_populates='workouts')


class UserProfile(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    email_address: str
    name: str
    birth_date: Optional[date]
    height_cm: Optional[int]
    updated_at: datetime = Field(default_factory=datetime.now)
    messages: List['ChatMessage'] = Relationship(back_populates='user')
    athlete_info: Optional['AthleteProfile'] = Relationship(back_populates='user')


class AthleteProfile(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, foreign_key='userprofile.id')
    weight_kg: Optional[float]
    current_FTP: Optional[int]
    limitations: Optional[Text]
    equipment_tracking: Optional[Text]  # какие устройства есть у пользователя
    weekly_hours: int  # Сколько времени есть на тренировки в неделю
    usual_stats: Optional[Text]  # какие показатели у него обычно
    weekly_routine: Optional[Text]  # Как обычно тренируется пользователь
    available_time: Optional[float]  # сколько времени хочет тратить на тренировки
    gear: Optional[Text]  # какое оборудование есть у пользователя( велосипед, станки..)
    environment_location: Optional[Text]  # окружение, локация
    user: Optional['UserProfile'] = Relationship(back_populates='athlete_info')


class ChatMessage(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key='userprofile.id')
    role: str  # user или assistant
    content: str
    created_at: datetime = Field(default_factory=datetime.now)
    user: Optional['UserProfile'] = Relationship(back_populates='messages')
