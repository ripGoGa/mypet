from datetime import timedelta
from typing import Sequence

import pytest
from app.models.models import Workout
from app.services.statistics_service import StatisticsService


class FakeWorkoutRepository:

    def __init__(self, test_workouts: Sequence[Workout]):
        self.history = []
        self.test_workouts = test_workouts

    def get_statistic_workouts(self, user_id: int, period: int = 0) -> Sequence[Workout]:
        self.history.append((user_id, period))
        return self.test_workouts


@pytest.fixture()
def test_workouts():
    user_id = 42
    result = [
        Workout(
            id=1,
            user_id=user_id,
            duration=timedelta(hours=1),
            moving_time=timedelta(minutes=55),
            distance_km=30.5,
            avg_watts=180,
            normalized_power=195.0,
            intensity_factor=0.72,
            training_stress_score=45.0,
            avg_cadence=85,
            avg_speed=33.2,
            avg_speed_without_stop=34,
            avg_heartrate=140,
            max_heartrate=165,
            calories_burned=650,
        ),
        Workout(
            id=2,
            user_id=user_id,
            duration=timedelta(hours=1, minutes=30),
            moving_time=timedelta(hours=1, minutes=20),
            distance_km=45.0,
            avg_watts=210,
            normalized_power=225.0,
            intensity_factor=0.84,
            training_stress_score=85.0,
            avg_cadence=88,
            avg_speed=33.8,
            avg_speed_without_stop=35,
            avg_heartrate=150,
            max_heartrate=178,
            calories_burned=900,
        ),
        Workout(
            id=3,
            user_id=user_id,
            duration=timedelta(hours=2),
            moving_time=timedelta(hours=1, minutes=50),
            distance_km=70.0,
            avg_watts=160,
            normalized_power=175.0,
            intensity_factor=0.65,
            training_stress_score=60.0,
            avg_cadence=82,
            avg_speed=38.2,
            avg_speed_without_stop=39,
            avg_heartrate=135,
            max_heartrate=160,
            calories_burned=1200,
        ),
        Workout(
            id=4,
            user_id=user_id,
            duration=timedelta(minutes=45),
            moving_time=timedelta(minutes=42),
            distance_km=20.0,
            avg_watts=250,
            normalized_power=270.0,
            intensity_factor=0.95,
            training_stress_score=110.0,
            avg_cadence=92,
            avg_speed=28.6,
            avg_speed_without_stop=29,
            avg_heartrate=165,
            max_heartrate=185,
            calories_burned=550,
        ),
        Workout(
            id=5,
            user_id=user_id,
            duration=timedelta(hours=1, minutes=15),
            moving_time=timedelta(hours=1, minutes=10),
            distance_km=40.0,
            avg_watts=190,
            normalized_power=205.0,
            intensity_factor=0.78,
            training_stress_score=75.0,
            avg_cadence=87,
            avg_speed=34.3,
            avg_speed_without_stop=35,
            avg_heartrate=145,
            max_heartrate=172,
            calories_burned=800,
        ),
    ]
    return result


@pytest.fixture()
def workout_repo(test_workouts) -> FakeWorkoutRepository:
    repo = FakeWorkoutRepository(test_workouts)
    return repo


@pytest.fixture()
def get_fake_statistic_service(workout_repo: FakeWorkoutRepository) -> StatisticsService:
    return StatisticsService(workout_repo=workout_repo)

@pytest.fixture()
def empty_workout_repo():
    return FakeWorkoutRepository(test_workouts=[])