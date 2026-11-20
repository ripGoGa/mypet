from datetime import UTC, datetime, timedelta

from app.models import CyclingWorkout, RunningWorkout
from app.models.models import Workout


def make_workout(**overrides) -> Workout:
    data = {
        "id": 11,
        "sport": "running",
        "started_at": datetime(2026, 10, 1, 7, 30, tzinfo=UTC),
        "duration": timedelta(hours=2, minutes=5),
        "source_file_id": 21,
        "user_id": 1,
    }
    unknown = overrides.keys() - data.keys()
    if unknown:
        raise ValueError(f"Unknown Workout fields: {unknown}")
    data.update(overrides)
    return Workout(**data)


def make_cycling_workout(**overrides) -> CyclingWorkout:
    data = {
        "id": 30,
        "workout_id": 11,
        "moving_time": timedelta(hours=1, minutes=55),
        "avg_altitude": 120.5,
        "avg_cadence": 87,
        "avg_grade": 1.2,
        "avg_heart_rate": 142,
        "avg_power": 195,
        "avg_speed": 28.4,
        "avg_temperature": 24,
        "max_altitude": 310.0,
        "max_cadence": 112,
        "max_heart_rate": 171,
        "max_power": 640,
        "max_speed": 58.2,
        "max_temperature": 29,
        "intensity_factor": 0.78,
        "left_right_balance": 0.51,
        "normalized_power": 212,
        "threshold_power": 270,
        "total_ascent": 820.0,
        "total_descent": 815.0,
        "total_distance": 56.3,
        "total_calories": 1450,
        "training_stress_score": 118.0,
    }
    unknown = overrides.keys() - data.keys()
    if unknown:
        raise ValueError(f"Unknown CyclingWorkout fields: {unknown}")
    data.update(overrides)
    return CyclingWorkout(**data)


def make_running_workout(**overrides) -> RunningWorkout:
    data = {
        "id": 40,
        "workout_id": 11,
        "avg_heart_rate": 151,
        "avg_power": 245,
        "avg_running_cadence": 86,
        "avg_speed": 2.95,
        "avg_stance_time": 248.0,
        "avg_stance_time_balance": 49.6,
        "avg_step_length": 1185.0,
        "avg_temperature": 27,
        "avg_vertical_oscillation": 82.5,
        "avg_vertical_ratio": 7.1,
        "effort_pace": 2.91,
        "max_heart_rate": 176,
        "max_running_cadence": 96,
        "max_speed": 4.12,
        "total_ascent": 64.0,
        "total_descent": 61.0,
        "total_distance": 10.25,
        "total_calories": 712,
        "total_elapsed_time": 3530.5,
        "total_strides": 4980,
        "total_timer_time": 3474.0,
    }
    unknown = overrides.keys() - data.keys()
    if unknown:
        raise ValueError(f"Unknown RunningWorkout fields: {unknown}")
    data.update(overrides)
    return RunningWorkout(**data)
