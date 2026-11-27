from datetime import UTC, datetime, timedelta

from app.models.models import UploadedFile, Workout


def test_get_workouts_list_success(authorized_client, make_workout_and_cycling, test_user_id):
    make_workout_and_cycling(user_id=test_user_id)
    response = authorized_client.get("/workouts?limit=1&period=0")
    assert response.status_code == 200
    assert "Страница 1 из 3" in response.text
    assert "Cycling" in response.text


def test_workout_detail_success(authorized_client, make_workout_and_cycling, test_user_id):
    workouts = make_workout_and_cycling(user_id=test_user_id)

    response = authorized_client.get(f"/workouts/{workouts[0].id}")

    assert response.status_code == 200
    assert str(workouts[0].duration) in response.text
    assert "Велосипед" in response.text


def test_workout_returns_404_for_another_user(
    authorized_client, make_workout_and_cycling, test_user_id, second_user_id
):
    make_workout_and_cycling(user_id=test_user_id)
    second_user_workouts = make_workout_and_cycling(user_id=second_user_id, range_limit=10)

    response = authorized_client.get(f"/workouts/{second_user_workouts[0].id}")

    assert response.status_code == 404
    assert "Тренировка не найдена" in response.text


def test_workout_returns_404_for_missing_workout(authorized_client, test_user_id, make_workout_and_cycling):
    make_workout_and_cycling(user_id=test_user_id, range_limit=10)

    response = authorized_client.get("/workouts/0")

    assert response.status_code == 404
    assert "Тренировка не найдена" in response.text


def test_workout_detail_returns_500_when_sport_record_unknow(
    authorized_client, test_user_id, db_test_session
):
    uploaded_file = UploadedFile(
        original_name="test_run",
        sha256="test_run",
        uploaded_at=datetime.now(UTC),
        user_id=test_user_id,
    )
    db_test_session.add(uploaded_file)
    db_test_session.commit()
    db_test_session.refresh(uploaded_file)

    workout = Workout(
        user_id=test_user_id,
        sport="swimming",
        duration=timedelta(hours=1),
        source_file_id=uploaded_file.id,
        started_at=datetime.now(UTC),
    )
    db_test_session.add(workout)
    db_test_session.commit()

    response = authorized_client.get(f"/workouts/{workout.id}")

    assert response.status_code == 500
    assert "Ошибка данных" in response.text
