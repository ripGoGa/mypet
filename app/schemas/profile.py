from pydantic import BaseModel
from typing import Optional
from datetime import date


class ProfileCreateDTO(BaseModel):
    name: str
    birth_date: Optional[date]
    height_cm: Optional[int]
    weight_kg: Optional[float]
    current_ftp: Optional[int]
    limitations: Optional[str]
    weekly_hours: Optional[float]
    gear: Optional[str]
    environment_location: Optional[str]
