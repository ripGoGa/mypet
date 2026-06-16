from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, timedelta


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


class WorkoutsDTO(BaseModel):
    count_workouts: int
    raw_total_distance: float
    total_tss_num: float
    total_moving_time: timedelta
    avg_watts_num: float
    avg_speed_num: float
    avg_heartrate_num: float
    max_in_factor: float
    max_distance: float
    max_np: float
    max_heartrate: float
    avg_cadence_num: float
    period: int
    total_ccall: float
    max_ccall: float
    raw_distance: float
    raw_tss: list[float]
    raw_watts: list[float]
    raw_speed: list[float]
    raw_heartrate: list[float]
    raw_cadence: list[float]
    raw_in_factor: list[float]
    raw_norm_power: list[float]
    raw_max_hr: list[float]
    raw_ccall: list[float]
    raw_chart_dates: list[str]
