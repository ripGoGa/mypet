import os
import shutil
import uuid
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, select

from app.db.session import get_session
from app.main import app
from app.models.models import AthleteProfile, UploadedFile, UserProfile, Users, Workout
from app.models.training_models import CyclingWorkout

pytest_plugins = (
    'app.tests.fixtures.coach',
    'app.tests.fixtures.statistics',
    'app.tests.fixtures.import'
)

ORIGINAL_DB_PATH = "data/app.db"
TEST_DB_PATH = "data/test_app.db"
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"

test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})


# МЕНЯЕМ НА scope="session" — фикстура сработает один раз для всей пачки тестов
@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except PermissionError:
            pass  # Если файл занят прошлым зависшим процессом

    if os.path.exists(ORIGINAL_DB_PATH):
        shutil.copyfile(ORIGINAL_DB_PATH, TEST_DB_PATH)
    else:
        raise FileNotFoundError(f"Не найден исходный файл базы данных: {ORIGINAL_DB_PATH}")

    def override_get_session():
        with Session(test_engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    yield  # Здесь прокрутятся все тесты

    app.dependency_overrides.clear()
    # Удаляем временный файл только после того, как ВСЕ тесты завершились
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except PermissionError:
            pass


@pytest.fixture()
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture()
def authorized_client(client):
    """"Создает авторизованного пользователя"""
    email = f'{uuid.uuid4()}@ya.ru'
    client.post('/register', data={'email': email, 'password': 'secure_pass'})
    client.post('/login', data={'username': email, 'password': 'secure_pass'})
    client.test_email = email
    yield client


@pytest.fixture()
def db_test_session():
    """"Создает подключение к тестовой базе"""
    with Session(test_engine) as session:
        yield session


@pytest.fixture()
def test_user_id(authorized_client, db_test_session, test_user):
    """Берем id у юзера для тестов"""
    user = test_user
    return user.id


@pytest.fixture()
def test_user(authorized_client, db_test_session):
    """Берем юзера для тестов"""
    user = db_test_session.exec(select(Users).where(Users.email == authorized_client.test_email)).first()
    return user


@pytest.fixture()
def load_athlete_profile(test_user_id, db_test_session) -> AthleteProfile:
    """Создаем спортивный профиль пользователя"""
    athlete = AthleteProfile(
        id=test_user_id,
        weight_kg=75.0,
        current_ftp=250,
        weekly_hours=8.5
    )
    db_test_session.add(athlete)
    db_test_session.commit()
    return athlete


@pytest.fixture()
def load_user_profile(test_user_id, db_test_session) -> UserProfile:
    """Создаем базовый профиль пользователя"""
    profile = UserProfile(
        id=test_user_id,
        name="Igor Test",
        birth_date=datetime(1992, 1, 1),
        height_cm=180
    )
    db_test_session.add(profile)
    db_test_session.commit()
    return profile


@pytest.fixture()
def load_workout_and_cycling(test_user_id, db_test_session):
    workouts = []
    for num in range(1, 31, 10):
        uploaded_file = UploadedFile(original_name='test_ride',
                                     sha256='test' + str(num),
                                     uploaded_at=datetime.now(UTC) - timedelta(days=num),
                                     user_id=test_user_id)
        db_test_session.add(uploaded_file)
        db_test_session.commit()
        db_test_session.refresh(uploaded_file)
        workout = Workout(sport = 'cycling',
                          started_at = datetime.now(UTC) - timedelta(days=num),
                          duration = timedelta(minutes=1 + num),

                          user_id = test_user_id,
                          source_file_id = uploaded_file.id
                          )
        db_test_session.add(workout)
        db_test_session.commit()
        workouts.append(workout)
        cycling = CyclingWorkout(workout_id = workout.id,
                                 moving_time = workout.duration,
                                 avg_altitude = 10 + num,
                                 avg_cadence = 60 + num,
                                 avg_grade = 2 + num // 5,
                                 avg_heart_rate = 110 + num,
                                 avg_power = 120 + num,
                                 avg_speed = 20 + num // 3,
                                 avg_temperature = 5 + num,
                                 max_altitude = 20 + num,
                                 max_cadence = 70 + num,
                                 max_heart_rate = 130 + num,
                                 max_power = 200 + num,
                                 max_speed = 30 + num,
                                 max_temperature = 10 + num,
                                 intensity_factor = 2 + num // 5,
                                 left_right_balance = 0.49,
                                 normalized_power = 130 + num,
                                 threshold_power = 120 + num,
                                 total_ascent = 40 + num,
                                 total_descent = 50 + num,
                                 total_distance = 60 + num,
                                 total_calories = 1000 + num,
                                 training_stress_score = 80.0 + num
                                 )
        db_test_session.add(cycling)
        db_test_session.commit()
    return workouts
