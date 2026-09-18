from datetime import timedelta
from typing import Sequence

import pytest

from app.models import CyclingWorkout
from app.models.models import Workout
from app.services.statistics_service import StatisticsService


class FakeCyclingWorkoutRepository:

    def __init__(self, test_workouts: Sequence[Workout], test_cycling_workouts: Sequence[CyclingWorkout]):
        self.history = []
        self.test_workouts = test_workouts
        self.test_cycling_workouts = test_cycling_workouts

    def get_statistic_workouts(self, user_id: int, period: int = 0) -> Sequence[tuple[Workout, CyclingWorkout]]:
        self.history.append((user_id, period))
        return list(zip(self.test_workouts, self.test_cycling_workouts, strict=True))


@pytest.fixture()
def test_workouts():
    user_id = 42

    return [
        Workout(
            id=1,
            user_id=user_id,
            sport="cycling",
            duration=timedelta(hours=1),
        ),
        Workout(
            id=2,
            user_id=user_id,
            sport="cycling",
            duration=timedelta(hours=1, minutes=30),
        ),
        Workout(
            id=3,
            user_id=user_id,
            sport="cycling",
            duration=timedelta(hours=2),
        ),
        Workout(
            id=4,
            user_id=user_id,
            sport="cycling",
            duration=timedelta(minutes=45),
        ),
        Workout(
            id=5,
            user_id=user_id,
            sport="cycling",
            duration=timedelta(hours=1, minutes=15),
        ),
    ]


@pytest.fixture()
def test_cycling_workouts():
    return [
        CyclingWorkout(
            id=1,
            workout_id=1,
            moving_time=timedelta(minutes=55),
            avg_power=180,
            normalized_power=195,
            intensity_factor=0.72,
            training_stress_score=45.0,
            avg_cadence=85,
            avg_speed=33.2,
            avg_heart_rate=140,
            max_heart_rate=165,
            total_distance=30.5,
            total_calories=650,
        ),
        CyclingWorkout(
            id=2,
            workout_id=2,
            moving_time=timedelta(hours=1, minutes=20),
            avg_power=210,
            normalized_power=225,
            intensity_factor=0.84,
            training_stress_score=85.0,
            avg_cadence=88,
            avg_speed=33.8,
            avg_heart_rate=150,
            max_heart_rate=178,
            total_distance=45.0,
            total_calories=900,
        ),
        CyclingWorkout(
            id=3,
            workout_id=3,
            moving_time=timedelta(hours=1, minutes=50),
            avg_power=160,
            normalized_power=175,
            intensity_factor=0.65,
            training_stress_score=60.0,
            avg_cadence=82,
            avg_speed=38.2,
            avg_heart_rate=135,
            max_heart_rate=160,
            total_distance=70.0,
            total_calories=1200,
        ),
        CyclingWorkout(
            id=4,
            workout_id=4,
            moving_time=timedelta(minutes=42),
            avg_power=250,
            normalized_power=270,
            intensity_factor=0.95,
            training_stress_score=110.0,
            avg_cadence=92,
            avg_speed=28.6,
            avg_heart_rate=165,
            max_heart_rate=185,
            total_distance=20.0,
            total_calories=550,
        ),
        CyclingWorkout(
            id=5,
            workout_id=5,
            moving_time=timedelta(hours=1, minutes=10),
            avg_power=190,
            normalized_power=205,
            intensity_factor=0.78,
            training_stress_score=75.0,
            avg_cadence=87,
            avg_speed=34.3,
            avg_heart_rate=145,
            max_heart_rate=172,
            total_distance=40.0,
            total_calories=800,
        ),
    ]


@pytest.fixture()
def get_fake_cycling_w_repo(test_workouts, test_cycling_workouts) -> FakeCyclingWorkoutRepository:
    repo = FakeCyclingWorkoutRepository(test_workouts, test_cycling_workouts)
    return repo


@pytest.fixture()
def get_fake_statistic_service(get_fake_cycling_w_repo: FakeCyclingWorkoutRepository) -> StatisticsService:
    return StatisticsService(cycling_repo=get_fake_cycling_w_repo, workout_repo=None)

@pytest.fixture()
def empty_cycling_workout_repo():
    return FakeCyclingWorkoutRepository(test_workouts=[], test_cycling_workouts= [])