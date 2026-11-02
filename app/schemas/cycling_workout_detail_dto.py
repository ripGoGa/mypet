from datetime import datetime, timedelta
from typing import Literal

from pydantic import BaseModel


class CyclingWorkoutDetailDTO(BaseModel):
    workout_id: int
    sport: Literal["cycling"]
    started_at: datetime
    source_file_id: int

    distance: float
    duration: timedelta
    tss: float | None
    moving_time: timedelta
    avg_watts: float | None
    avg_speed: float
    avg_heartrate: float | None
    intensity_factor: float | None
    normalized_power: float | None
    max_heartrate: float | None
    avg_cadence: float | None
    calories: float | None
    max_cadence: float | None
    training_intensity: Literal["light", "medium", "hard"] | None
