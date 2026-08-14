from datetime import date, timedelta
from typing import Optional

from pydantic import BaseModel, Field


class ProfileCreateDTO(BaseModel):
    name: str
    birth_date: Optional[date]
    height_cm: Optional[int] = Field(default=None, ge=30, lt=220, description='Рост в см')
    weight_kg: Optional[float] = Field(default=None, ge=20, lt=299, description='Вес в кг')
    current_ftp: Optional[int] = Field(default=None, ge=0, description='Мощность в вт')
    limitations: Optional[str]
    weekly_hours: Optional[float] = Field(default=None, ge=0, description='Время в часах')
    gear: Optional[str]
    environment_location: Optional[str]

