from app.schemas.workoutDTO import WorkoutsDTO
from app.services.statistics_service import StatisticsService
from app.tests.fixtures.statistics import FakeCyclingWorkoutRepository


def test_get_user_stats_success(test_workouts, get_fake_cycling_w_repo: FakeCyclingWorkoutRepository,
                                get_fake_statistic_service: StatisticsService):
    result = get_fake_statistic_service.get_user_stats(user_id=42, period=7)
    assert isinstance(result, WorkoutsDTO)
    assert get_fake_cycling_w_repo.history == [(42, 7)]
    assert result.count_workouts == len(test_workouts)


def test_zero_workout_stats(empty_cycling_workout_repo):
    result = StatisticsService(cycling_repo=empty_cycling_workout_repo,
                               workout_repo=None).get_user_stats(user_id=1)
    assert isinstance(result, WorkoutsDTO)
    assert result.count_workouts == 0



