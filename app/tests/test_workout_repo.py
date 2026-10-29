from app.repository.workout_repo import WorkoutRepository


def test_workout_repo_get_workouts_includes_all_sports(
    db_test_session, test_user_id, make_workout_and_running, make_workout_and_cycling
):
    make_workout_and_running(user_id=test_user_id, range_limit=51)
    make_workout_and_cycling(user_id=test_user_id, range_limit=91)
    workout_repo = WorkoutRepository(db_test_session)

    workouts, count = workout_repo.get_workouts(test_user_id, limit=100, offset=0, period=0)

    assert count == 14, count
    assert {w.sport for w in workouts} == {"cycling", "running"}


def test_workout_repo_get_workouts_own_workout(
    db_test_session, test_user_id, make_workout_and_cycling, make_workout_and_running, second_user_id
):
    make_workout_and_cycling(user_id=test_user_id, range_limit=31)
    make_workout_and_running(user_id=test_user_id, range_limit=31)
    make_workout_and_running(user_id=second_user_id, range_limit=11)
    make_workout_and_cycling(user_id=second_user_id, range_limit=11)
    workout_repo = WorkoutRepository(db_test_session)

    workout, count = workout_repo.get_workouts(test_user_id, limit=100, offset=0, period=0)

    assert count == 6, count
    assert {w.user_id for w in workout} == {test_user_id}


def test_workout_repo_get_workouts_right_order(db_test_session, test_user_id, make_workout_and_cycling):
    make_workout_and_cycling(user_id=test_user_id, range_limit=221)
    workout_repo = WorkoutRepository(db_test_session)

    workout, count = workout_repo.get_workouts(test_user_id, limit=100, offset=0, period=0)

    assert workout == sorted(workout, key=lambda w: w.started_at, reverse=True)


def test_workout_repo_get_workouts_limit_paginated(
    db_test_session, test_user_id, make_workout_and_cycling, make_workout_and_running
):
    make_workout_and_cycling(user_id=test_user_id, range_limit=61)
    make_workout_and_running(user_id=test_user_id, range_limit=101)
    workout_repo = WorkoutRepository(db_test_session)
    limit = 10

    workout, count = workout_repo.get_workouts(user_id=test_user_id, limit=limit, offset=0, period=0)

    assert len(workout) == limit, len(workout)
    assert count == 16


def test_workout_repo_get_workouts_offset_paginated(
    db_test_session, test_user_id, make_workout_and_cycling, make_workout_and_running
):
    make_workout_and_cycling(user_id=test_user_id, range_limit=61)
    make_workout_and_running(user_id=test_user_id, range_limit=101)
    workout_repo = WorkoutRepository(db_test_session)

    workout_page1, count_page1 = workout_repo.get_workouts(user_id=test_user_id, limit=10, offset=0, period=0)
    workout_page2, count_page2 = workout_repo.get_workouts(user_id=test_user_id, limit=10, offset=10, period=0)
    workout_page3, count_page3 = workout_repo.get_workouts(user_id=test_user_id, limit=10, offset=20, period=0)
    assert count_page1 == count_page2 == count_page3 == 16
    assert len(workout_page1) == 10, len(workout_page1)
    assert len(workout_page2) == 6, len(workout_page2)
    assert len(workout_page3) == 0, len(workout_page3)


def test_workout_repo_get_workouts_period(
    db_test_session, test_user_id, make_workout_and_cycling, make_workout_and_running
):
    make_workout_and_cycling(user_id=test_user_id, range_limit=31)
    make_workout_and_running(user_id=test_user_id, range_limit=31)
    workout_repo = WorkoutRepository(db_test_session)

    workouts, count = workout_repo.get_workouts(user_id=test_user_id, limit=100, offset=0, period=15)

    assert count == 4, count
    assert len(workouts) == 4, len(workouts)


def test_workout_repo_get_workouts_empty(db_test_session, test_user_id):
    workout_repo = WorkoutRepository(db_test_session)

    workouts, count = workout_repo.get_workouts(user_id=test_user_id, limit=100, offset=0, period=0)

    assert len(workouts) == 0, len(workouts)
    assert count == 0, count
