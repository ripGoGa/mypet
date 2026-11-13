from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from app.models import RunningWorkout
from app.models.models import Workout
from app.schemas.running_workout_detail_dto import RunningWorkoutDetailDTO


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


def test_running_workout_dto_rejects_missing_timer_time() -> None:
    workout = make_workout()
    running_workout = make_running_workout(total_timer_time=None)

    with pytest.raises(ValidationError, match="moving_time"):
        RunningWorkoutDetailDTO.from_models(workout, running_workout)


def test_running_workout_dto_copies_fields_from_models() -> None:
    workout = make_workout()
    running_workout = make_running_workout()

    running_detail_dto = RunningWorkoutDetailDTO.from_models(workout, running_workout)

    assert running_detail_dto.workout_id == workout.id
    assert running_detail_dto.sport == workout.sport
    assert running_detail_dto.started_at == workout.started_at
    assert running_detail_dto.duration == workout.duration
    assert running_detail_dto.source_file_id == workout.source_file_id
    assert running_detail_dto.distance == running_workout.total_distance
    assert running_detail_dto.calories == running_workout.total_calories
    assert running_detail_dto.avg_heartrate == running_workout.avg_heart_rate
    assert running_detail_dto.max_heartrate == running_workout.max_heart_rate
    assert running_detail_dto.avg_speed == running_workout.avg_speed
    assert running_detail_dto.avg_cadence == 172
    assert running_detail_dto.moving_time == timedelta(seconds=3474.0)


def test_running_workout_dto_fields_are_none() -> None:
    workout = make_workout()
    running_workout = make_running_workout(
        avg_running_cadence=0,
        avg_speed=None,
        total_distance=None,
        avg_heart_rate=None,
        max_heart_rate=None,
        total_calories=None,
    )

    running_detail_dto = RunningWorkoutDetailDTO.from_models(workout, running_workout)

    assert running_detail_dto.avg_cadence is None
    assert running_detail_dto.avg_speed is None
    assert running_detail_dto.max_heartrate is None
    assert running_detail_dto.avg_heartrate is None
    assert running_detail_dto.distance is None
    assert running_detail_dto.calories is None


def test_running_workout_dto_wrong_type_of_sport() -> None:
    workout = make_workout(sport="cycling")
    running_workout = make_running_workout()

    with pytest.raises(ValidationError, match="sport"):
        RunningWorkoutDetailDTO.from_models(workout, running_workout)
