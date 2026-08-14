from types import NoneType

from app.schemas.workoutDTO import WorkoutsDTO
from app.services.statistics_service import StatisticsService
from app.tests.conftest import FakeWorkoutRepository


def test_get_user_stats_success(test_workouts, workout_repo: FakeWorkoutRepository,
                                get_fake_statistic_service: StatisticsService):
    result = get_fake_statistic_service.get_user_stats(user_id=42, period=7)
    assert isinstance(result, WorkoutsDTO)
    assert workout_repo.history == [(42, 7)]
    assert result.count_workouts == len(test_workouts)


def test_zero_workout_stats(empty_workout_repo):
    result = StatisticsService(workout_repo=empty_workout_repo).get_user_stats(user_id=1)
    assert isinstance(result, WorkoutsDTO)
    assert result.count_workouts == 0

def test_list_workouts(authorized_client, load_workout):
    authorized_client.get(url='')

