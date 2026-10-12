from datetime import timedelta
from typing import Sequence

import pytest

from app.models import CyclingWorkout
from app.models.models import Workout
from app.models.training_models import RunningWorkout
from app.services.statistics_service import StatisticsService


class FakeCyclingWorkoutRepository:
    def __init__(self, test_workouts: Sequence[Workout], test_cycling_workouts: Sequence[CyclingWorkout]):
        self.history = []
        self.test_workouts = test_workouts
        self.test_cycling_workouts = test_cycling_workouts

    def get_statistic_workouts(
        self, user_id: int, period: int = 0
    ) -> Sequence[tuple[Workout, CyclingWorkout]]:
        self.history.append((user_id, period))
        return list(zip(self.test_workouts, self.test_cycling_workouts, strict=True))


class FakeRunningWorkoutRepository:
    def __init__(
        self,
        test_workouts: Sequence[Workout],
        test_running_workouts: Sequence[RunningWorkout],
    ):
        self.history = []
        self.test_workouts = test_workouts
        self.test_running_workouts = test_running_workouts

    def get_statistic_workouts(
        self, user_id: int, period: int = 0
    ) -> Sequence[tuple[Workout, RunningWorkout]]:
        self.history.append((user_id, period))
        return list(zip(self.test_workouts, self.test_running_workouts, strict=True))


@pytest.fixture()
def test_workouts_for_cycling():
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
def test_workouts_for_running():
    user_id = 42
    return [
        Workout(
            id=6,
            user_id=user_id,
            sport="running",
            duration=timedelta(hours=2),
        ),
        Workout(
            id=7,
            user_id=user_id,
            sport="running",
            duration=timedelta(minutes=45),
        ),
        Workout(
            id=8,
            user_id=user_id,
            sport="running",
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
def test_running_workouts():
    return [
        RunningWorkout(
            id=6,
            workout_id=6,
            total_elapsed_time=2400.41,
            total_timer_time=2400.0,
            total_distance=6.11,
            total_calories=376,
            max_heart_rate=139,
            min_heart_rate=64,
            avg_heart_rate=124,
            avg_temperature=32,
            total_ascent=0,
            total_descent=5,
            total_strides=3536,
            max_running_cadence=91,
            avg_running_cadence=88,
            avg_step_length=870.0,
            enhanced_max_speed=2.857,
            max_speed=2.857,
            enhanced_avg_speed=2.547,
            avg_speed=2.547,
            avg_power=189,
            avg_stance_time=254.0,
            avg_stance_time_balance=0.0,
            avg_vertical_oscillation=76.0,
            avg_vertical_ratio=8.7,
        ),
        RunningWorkout(
            id=7,
            workout_id=7,
            total_elapsed_time=2400.41,
            total_timer_time=2400.0,
            total_distance=6.11,
            total_calories=376,
            max_heart_rate=139,
            min_heart_rate=64,
            avg_heart_rate=124,
            avg_temperature=32,
            total_ascent=0,
            total_descent=5,
            total_strides=3536,
            max_running_cadence=91,
            avg_running_cadence=88,
            avg_step_length=870.0,
            enhanced_max_speed=2.857,
            max_speed=2.857,
            enhanced_avg_speed=2.547,
            avg_speed=2.547,
            avg_power=189,
            avg_stance_time=254.0,
            avg_stance_time_balance=0.0,
            avg_vertical_oscillation=76.0,
            avg_vertical_ratio=8.7,
        ),
        RunningWorkout(
            id=8,
            workout_id=8,
            total_elapsed_time=2410.41,
            total_timer_time=2410.0,
            total_distance=6.12,
            total_calories=386,
            max_heart_rate=139,
            min_heart_rate=70,
            avg_heart_rate=128,
            avg_temperature=33,
            total_ascent=1,
            total_descent=5,
            total_strides=3544,
            max_running_cadence=96,
            avg_running_cadence=89,
            avg_step_length=871.0,
            enhanced_max_speed=2.867,
            max_speed=2.957,
            enhanced_avg_speed=2.847,
            avg_speed=2.547,
            avg_power=190,
            avg_stance_time=253.0,
            avg_stance_time_balance=0.0,
            avg_vertical_oscillation=75.0,
            avg_vertical_ratio=8.6,
        ),
    ]


@pytest.fixture()
def get_fake_cycling_w_repo(test_workouts_for_cycling, test_cycling_workouts) -> FakeCyclingWorkoutRepository:
    repo = FakeCyclingWorkoutRepository(test_workouts_for_cycling, test_cycling_workouts)
    return repo


@pytest.fixture()
def get_fake_running_w_repo(test_workouts_for_running, test_running_workouts) -> FakeRunningWorkoutRepository:
    repo = FakeRunningWorkoutRepository(test_workouts_for_running, test_running_workouts)
    return repo


@pytest.fixture()
def get_fake_statistic_service(
    get_fake_cycling_w_repo: FakeCyclingWorkoutRepository,
    get_fake_running_w_repo: FakeRunningWorkoutRepository,
) -> StatisticsService:
    return StatisticsService(cycling_repo=get_fake_cycling_w_repo, running_repo=get_fake_running_w_repo)


@pytest.fixture()
def empty_cycling_workout_repo():
    return FakeCyclingWorkoutRepository(test_workouts=[], test_cycling_workouts=[])


@pytest.fixture()
def empty_running_workout_repo():
    return FakeRunningWorkoutRepository(test_workouts=[], test_running_workouts=[])
