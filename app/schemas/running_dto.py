from datetime import timedelta

from pydantic import BaseModel


class RunningStatsDTO(BaseModel):
    total_distance: float
    total_ccall: float
    total_moving_time: timedelta

    avg_cadence_num: float
    avg_speed_num: float
    avg_heartrate_num: float

    max_distance: float
    max_heartrate: float
    max_ccall: float

    raw_distance: list[float| None]
    raw_speed: list[float| None]
    raw_heartrate: list[float| None]
    raw_cadence: list[float| None]
    raw_max_hr: list[float| None]
    raw_ccall: list[float| None]
    raw_chart_dates: list[str]

    count_workouts: int
