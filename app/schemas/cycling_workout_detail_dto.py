from datetime import datetime, timedelta
from typing import Literal, Self

from pydantic import BaseModel

from app.core.cycling_training_intensity import classify_training_intensity
from app.models import CyclingWorkout
from app.models.models import Workout


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

    @classmethod
    def from_models(cls, workout: Workout, cycling: CyclingWorkout) -> Self:
        return cls(
            workout_id=workout.id,
            sport=workout.sport,
            started_at=workout.started_at,
            source_file_id=workout.source_file_id,
            distance=cycling.total_distance,
            duration=workout.duration,
            tss=cycling.training_stress_score,
            moving_time=cycling.moving_time,
            avg_watts=cycling.avg_power,
            avg_speed=cycling.avg_speed,
            avg_heartrate=cycling.avg_heart_rate,
            intensity_factor=cycling.intensity_factor,
            normalized_power=cycling.normalized_power,
            max_heartrate=cycling.max_heart_rate,
            avg_cadence=cycling.avg_cadence,
            calories=cycling.total_calories,
            max_cadence=cycling.max_cadence,
            training_intensity=classify_training_intensity(cycling.training_stress_score),
        )
