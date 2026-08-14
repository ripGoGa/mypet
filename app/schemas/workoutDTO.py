from datetime import timedelta

from pydantic import BaseModel


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
    total_ccall: float
    max_ccall: float
    raw_distance: list[float]
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