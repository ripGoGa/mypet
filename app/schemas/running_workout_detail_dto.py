from datetime import datetime, timedelta
from typing import Literal, Self

from pydantic import BaseModel

from app.models import RunningWorkout
from app.models.models import Workout


class RunningWorkoutDetailDTO(BaseModel):
    workout_id: int
    sport: Literal["running"]
    started_at: datetime
    source_file_id: int

    distance: float | None
    duration: timedelta
    calories: float | None
    moving_time: timedelta
    avg_cadence: float | None  # шагов в минуту, обе ноги (FIT хранит на одну, умножаем при сборке)
    avg_speed: float | None  # Хранится как м/с, но выводится уже как время на км.
    avg_heartrate: float | None
    max_heartrate: float | None

    @classmethod
    def from_models(cls, workout: Workout, running: RunningWorkout) -> Self:
        return cls(
            workout_id=workout.id,
            sport=workout.sport,
            started_at=workout.started_at,
            source_file_id=workout.source_file_id,
            distance=running.total_distance,
            duration=workout.duration,
            moving_time=timedelta(seconds=running.total_timer_time) if running.total_timer_time else None,
            avg_speed=running.avg_speed,
            avg_heartrate=running.avg_heart_rate,
            max_heartrate=running.max_heart_rate,
            avg_cadence=running.avg_running_cadence * 2 if running.avg_running_cadence else None,
            calories=running.total_calories,
        )
