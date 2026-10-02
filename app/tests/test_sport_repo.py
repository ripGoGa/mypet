from app.repository.cycling_repo import CyclingWorkoutRepository
from app.repository.running_repo import RunningWorkoutRepository


def test_get_workouts_total_count_respects_sport_and_period_success(
    db_test_session, test_user_id, make_workout_and_cycling, make_workout_and_running
):
    make_workout_and_cycling(user_id=test_user_id)
    make_workout_and_running(user_id=test_user_id)
    cycling_repo = CyclingWorkoutRepository(db_test_session)
    running_repo = RunningWorkoutRepository(db_test_session)
    cycling_workouts = cycling_repo.get_workouts(user_id=test_user_id, period=60, limit=10, offset=0)
    running_workouts = running_repo.get_workouts(user_id=test_user_id, period=20, limit=10, offset=0)
    assert running_workouts[1] == 2
    assert cycling_workouts[1] == 3


def test_get_workouts_total_count_excludes_other_users(
    db_test_session, test_user_id, second_user_id, make_workout_and_cycling, make_workout_and_running
):
    make_workout_and_cycling(user_id=test_user_id, range_limit=30)
    make_workout_and_running(user_id=test_user_id, range_limit=10)

    make_workout_and_cycling(user_id=second_user_id, range_limit=10)
    make_workout_and_running(user_id=second_user_id, range_limit=30)

    cycling_repo = CyclingWorkoutRepository(db_test_session)
    running_repo = RunningWorkoutRepository(db_test_session)
    cycling_workouts_test_user = cycling_repo.get_workouts(user_id=test_user_id, limit=10, offset=0, period=60)
    cycling_workouts_other_user = cycling_repo.get_workouts(
        user_id=second_user_id, limit=10, offset=0, period=30
    )
    running_workouts_test_user = running_repo.get_workouts(user_id=test_user_id, limit=10, offset=0, period=60)
    running_workouts_other_user = running_repo.get_workouts(
        user_id=second_user_id, limit=10, offset=0, period=30
    )
    assert cycling_workouts_test_user[1] == 3
    assert running_workouts_test_user[1] == 1

    assert cycling_workouts_other_user[1] == 1
    assert running_workouts_other_user[1] == 3
