from datetime import timedelta

import pytest
from pydantic import ValidationError

from app.schemas.running_workout_detail_dto import RunningWorkoutDetailDTO
from app.tests.fixtures.model_factories import make_running_workout, make_workout


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
