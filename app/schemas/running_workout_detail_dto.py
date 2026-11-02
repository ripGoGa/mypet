from datetime import datetime, timedelta
from typing import Literal

from pydantic import BaseModel


class RunningWorkoutDetailDTO(BaseModel):
    workout_id: int
    sport: Literal["running"]
    started_at: datetime
    source_file_id: int

    distance: float | None
    duration: timedelta
    calories: float | None
    moving_time: timedelta | None
    avg_cadence: float | None  # Значение умножается на 2
    avg_speed: float | None  # Хранится как м\с, но выводится уже как время на км.
    avg_heartrate: float | None
    max_heartrate: float | None
