from datetime import timedelta
from typing import Optional

from sqlmodel import Field, SQLModel


class CyclingWorkout(SQLModel, table=True):
    id: int = Field(primary_key=True, default=None)
    workout_id: int = Field(foreign_key="workout.id", unique=True)

    moving_time: timedelta
    avg_altitude: Optional[float]
    avg_cadence: Optional[int]
    avg_grade: Optional[float]
    avg_heart_rate: Optional[int]
    avg_power: Optional[int]
    avg_speed: Optional[float]
    avg_temperature: Optional[int]

    max_altitude: Optional[float]
    max_cadence: Optional[int]
    max_heart_rate: Optional[int]
    max_power: Optional[int]
    max_speed: Optional[float]
    max_temperature: Optional[int]

    intensity_factor: Optional[float]
    left_right_balance: Optional[float]
    normalized_power: Optional[int]
    threshold_power: Optional[int]

    total_ascent: Optional[float]
    total_descent: Optional[float]
    total_distance: Optional[float]
    total_calories: Optional[int]

    training_stress_score: Optional[float]

class RunningWorkout(SQLModel, table=True):
    id: int = Field(primary_key=True, default=None)
    workout_id: int = Field(foreign_key="workout.id", unique=True)

    avg_heart_rate: Optional[int]
    avg_power: Optional[int]
    avg_running_cadence: Optional[int]
    avg_speed: Optional[float]
    avg_stance_time: Optional[float]
    avg_stance_time_balance: Optional[float]
    avg_step_length: Optional[float]
    avg_temperature: Optional[int]
    avg_vertical_oscillation: Optional[float]
    avg_vertical_ratio: Optional[float]
    effort_pace: Optional[float]

    max_heart_rate: Optional[int]
    max_running_cadence: Optional[int]
    max_speed: Optional[float]

    total_ascent: Optional[float]
    total_descent: Optional[float]
    total_distance: Optional[float]
    total_calories: Optional[int]
    total_elapsed_time: Optional[float]
    total_strides: Optional[int]
    total_timer_time: Optional[float]


