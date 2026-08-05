from app.schemas.workoutDTO import WorkoutsDTO


def test_get_user_stats_success(test_workouts, workout_repo, get_fake_statistic_service):
    result = get_fake_statistic_service.get_user_stats(user_id=42, period=7)
    assert isinstance(result, WorkoutsDTO)
    assert workout_repo.history == [(42, 7)]
    assert result.count_workouts == len(test_workouts)