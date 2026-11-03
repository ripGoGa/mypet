from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from app.models import CyclingWorkout
from app.models.models import Workout
from app.schemas.cycling_workout_detail_dto import CyclingWorkoutDetailDTO


def make_workout(**overrides) -> Workout:
    data = {
        "id": 10,
        "sport": "cycling",
        "started_at": datetime(2026, 10, 1, 7, 30, tzinfo=UTC),
        "duration": timedelta(hours=2, minutes=5),
        "source_file_id": 20,
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
        "workout_id": 10,
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


def test_cycling_workout_detail_dto_fields():
    workout = make_workout()
    cycling = make_cycling_workout()

    result = CyclingWorkoutDetailDTO.from_models(workout, cycling)

    assert result.workout_id == workout.id, result.workout_id
    assert result.avg_watts == cycling.avg_power, result.avg_watts
    assert result.tss == cycling.training_stress_score, result.tss
    assert result.calories == cycling.total_calories
    assert result.training_intensity == "hard", result.training_intensity


def test_cycling_workout_detail_dto_fields_none():
    workout = make_workout()
    cycling = make_cycling_workout(
        training_stress_score=None,
        avg_power=None,
        max_heart_rate=None,
        max_cadence=None,
    )

    result = CyclingWorkoutDetailDTO.from_models(workout, cycling)

    assert result.tss == cycling.training_stress_score, result.tss
    assert result.training_intensity is None
    assert result.max_cadence is None
    assert result.max_heartrate is None
    assert result.avg_watts is None


def test_cycling_workout_detail_dto_no_sport_fail():
    workout = make_workout(sport="running")
    cycling = make_cycling_workout()

    with pytest.raises(ValidationError, match="sport"):
        CyclingWorkoutDetailDTO.from_models(workout, cycling)
