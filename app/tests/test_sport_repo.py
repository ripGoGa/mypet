from app.models import CyclingWorkout, RunningWorkout
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
    cycling_workouts_other_user = cycling_repo.get_workouts(user_id=second_user_id, limit=10, offset=0, period=30)
    running_workouts_test_user = running_repo.get_workouts(user_id=test_user_id, limit=10, offset=0, period=60)
    running_workouts_other_user = running_repo.get_workouts(user_id=second_user_id, limit=10, offset=0, period=30)
    assert cycling_workouts_test_user[1] == 3
    assert running_workouts_test_user[1] == 1

    assert cycling_workouts_other_user[1] == 1
    assert running_workouts_other_user[1] == 3


def test_cycling_get_by_workout_id_returns_own_workout(db_test_session, test_user_id, make_workout_and_cycling):
    workouts = make_workout_and_cycling(user_id=test_user_id, range_limit=30)
    cycling_repo = CyclingWorkoutRepository(db_test_session)

    cycling_workout = cycling_repo.get_by_workout_id(workout_id=workouts[0].id, user_id=test_user_id)

    assert isinstance(cycling_workout, CyclingWorkout)
    assert cycling_workout.workout_id == workouts[0].id


def test_cycling_get_by_workout_id_returns_none_for_missing_id(db_test_session, test_user_id, make_workout_and_cycling):
    make_workout_and_cycling(user_id=test_user_id, range_limit=30)
    cycling_repo = CyclingWorkoutRepository(db_test_session)

    not_existed_workout = cycling_repo.get_by_workout_id(workout_id=0, user_id=test_user_id)

    assert not_existed_workout is None


def test_cycling_get_by_workout_id_returns_none_for_running_workout(
    db_test_session, test_user_id, make_workout_and_cycling, make_workout_and_running
):
    make_workout_and_cycling(user_id=test_user_id, range_limit=10)
    running_workouts = make_workout_and_running(user_id=test_user_id, range_limit=30)
    cycling_repo = CyclingWorkoutRepository(db_test_session)

    not_existed_cycling_workout = cycling_repo.get_by_workout_id(
        workout_id=running_workouts[0].id, user_id=test_user_id
    )

    assert not_existed_cycling_workout is None


def test_cycling_get_by_workout_id_returns_none_for_other_user(
    db_test_session, test_user_id, second_user_id, make_workout_and_cycling
):
    make_workout_and_cycling(user_id=test_user_id, range_limit=10)
    second_user_workout = make_workout_and_cycling(user_id=second_user_id, range_limit=31)
    cycling_repo = CyclingWorkoutRepository(db_test_session)

    get_second_user_workout = cycling_repo.get_by_workout_id(workout_id=second_user_workout[0].id, user_id=test_user_id)

    assert get_second_user_workout is None


def test_running_get_by_workout_id_returns_own_workout(db_test_session, test_user_id, make_workout_and_running):
    workouts = make_workout_and_running(user_id=test_user_id, range_limit=30)
    running_repo = RunningWorkoutRepository(db_test_session)

    running_workout = running_repo.get_by_workout_id(workout_id=workouts[0].id, user_id=test_user_id)

    assert isinstance(running_workout, RunningWorkout)
    assert running_workout.workout_id == workouts[0].id


def test_running_get_by_workout_id_returns_none_for_missing_id(db_test_session, test_user_id, make_workout_and_running):
    make_workout_and_running(user_id=test_user_id, range_limit=30)
    running_repo = RunningWorkoutRepository(db_test_session)

    not_existed_workout = running_repo.get_by_workout_id(workout_id=0, user_id=test_user_id)

    assert not_existed_workout is None


def test_running_get_by_workout_id_returns_none_for_cycling_workout(
    db_test_session, test_user_id, make_workout_and_cycling, make_workout_and_running
):
    make_workout_and_running(user_id=test_user_id, range_limit=10)
    cycling_workouts = make_workout_and_cycling(user_id=test_user_id, range_limit=30)
    running_repo = RunningWorkoutRepository(db_test_session)

    not_existed_running_workout = running_repo.get_by_workout_id(
        workout_id=cycling_workouts[0].id, user_id=test_user_id
    )

    assert not_existed_running_workout is None


def test_running_get_by_workout_id_returns_none_for_other_user(
    db_test_session, test_user_id, second_user_id, make_workout_and_running
):
    make_workout_and_running(user_id=test_user_id, range_limit=10)
    second_user_workout = make_workout_and_running(user_id=second_user_id, range_limit=31)
    running_repo = RunningWorkoutRepository(db_test_session)

    get_second_user_workout = running_repo.get_by_workout_id(workout_id=second_user_workout[0].id, user_id=test_user_id)

    assert get_second_user_workout is None
