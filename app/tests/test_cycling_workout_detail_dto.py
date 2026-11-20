import pytest
from pydantic import ValidationError

from app.schemas.cycling_workout_detail_dto import CyclingWorkoutDetailDTO
from app.tests.fixtures.model_factories import make_cycling_workout, make_workout


def test_cycling_workout_detail_dto_fields():
    workout = make_workout(sport="cycling")
    cycling = make_cycling_workout()

    result = CyclingWorkoutDetailDTO.from_models(workout, cycling)

    assert result.workout_id == workout.id, result.workout_id
    assert result.avg_watts == cycling.avg_power, result.avg_watts
    assert result.tss == cycling.training_stress_score, result.tss
    assert result.calories == cycling.total_calories
    assert result.training_intensity == "hard", result.training_intensity


def test_cycling_workout_detail_dto_fields_none():
    workout = make_workout(sport="cycling")
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
