import os
import shutil
from datetime import datetime, UTC, timedelta

import pytest
from sqlmodel import Session, create_engine, select
from app.main import app
from app.db.session import get_session
from fastapi.testclient import TestClient

from app.models.models import Users, UserProfile, AthleteProfile, UploadedFile, Workout

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
    client.post('/register', data={'email': 'test_client@ya.ru', 'password': 'secure_pass'})
    client.post('/login', data={'username': 'test_client@ya.ru', 'password': 'secure_pass'})
    yield client


@pytest.fixture()
def db_test_session():
    """"Создает подключение к тестовой базе"""
    with Session(test_engine) as session:
        yield session


@pytest.fixture()
def test_user_id(authorized_client, db_test_session):
    """Берем id у юзера для тестов"""
    user = db_test_session.exec(select(Users).where(Users.email == 'test_client@ya.ru')).first()
    return user.id


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
def load_workout(test_user_id, db_test_session):
    workouts = []
    for num in range(1, 31, 10):
        uploaded_file = UploadedFile(original_name='test_ride',
                                     sha256='test' + str(num),
                                     uploaded_at=datetime.now(UTC) - timedelta(days=num),
                                     user_id=test_user_id)
        db_test_session.add(uploaded_file)
        db_test_session.commit()
        db_test_session.refresh(uploaded_file)
        workout = Workout(duration=timedelta(hours=1, minutes=30) + timedelta(minutes=num),
                          moving_time=timedelta(hours=1, minutes=30),
                          distance_km=45,
                          source_file_id=uploaded_file.id,
                          user_id=test_user_id
                          )
        db_test_session.add(workout)
        db_test_session.commit()
        workouts.append(workout)
    return workouts
