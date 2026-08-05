import os
import shutil
import uuid
from datetime import datetime, UTC, timedelta
from typing import Sequence

import pytest
from fastapi import Depends
from sqlmodel import Session, create_engine, select

from app.core.exceptions import AIProviderNotAvailable
from app.infrastructure.llm.ollama_provider import OllamaProvider
from app.main import app
from app.db.session import get_session
from fastapi.testclient import TestClient

from app.models.models import Users, UserProfile, AthleteProfile, UploadedFile, Workout
from app.repository.chat_repo import ChatRepository
from app.repository.workout_repo import WorkoutRepository
from app.services.coach_service import CoachService
from app.services.statistics_service import StatisticsService

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
    """Берем id у юзера для тестов"""
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


class FakeLLMProvider:
    def __init__(self):
        self.history_messages = []

    async def send_message(self, messages: list[dict[str, str]]) -> str:
        self.history_messages.append(messages)
        return 'Ответ LLM'


class BrokenFakeLLMProvider:
    def __init__(self):
        self.history_messages = []

    async def send_message(self, messages: list[dict[str, str]]) -> str:
        self.history_messages.append(messages)
        raise AIProviderNotAvailable


@pytest.fixture()
def fake_llm_provider():
    return FakeLLMProvider()


@pytest.fixture()
def get_test_coach_service(db_test_session) -> CoachService:
    workout_repo = WorkoutRepository(session=db_test_session)
    chat_repo = ChatRepository(session=db_test_session)
    llm_provider = FakeLLMProvider()
    new_coach_service = CoachService(workout_repo=workout_repo, chat_repo=chat_repo, llm_provider=llm_provider)
    return new_coach_service


@pytest.fixture()
def get_test_broken_coach_service(db_test_session) -> CoachService:
    workout_repo = WorkoutRepository(session=db_test_session)
    chat_repo = ChatRepository(session=db_test_session)
    llm_provider = BrokenFakeLLMProvider()
    new_coach_service = CoachService(workout_repo=workout_repo, chat_repo=chat_repo, llm_provider=llm_provider)
    return new_coach_service


class FakeWorkoutRepository:

    def __init__(self, test_workouts: Sequence[Workout]):
        self.history = []
        self.test_workouts = test_workouts

    def get_statistic_workouts(self, user_id: int, period: int = 0) -> Sequence[Workout]:
        self.history.append((user_id, period))
        return self.test_workouts


@pytest.fixture()
def test_workouts():
    user_id = 42
    result = [
        Workout(
            id=1,
            user_id=user_id,
            duration=timedelta(hours=1),
            moving_time=timedelta(minutes=55),
            distance_km=30.5,
            avg_watts=180,
            normalized_power=195.0,
            intensity_factor=0.72,
            training_stress_score=45.0,
            avg_cadence=85,
            avg_speed=33.2,
            avg_speed_without_stop=34,
            avg_heartrate=140,
            max_heartrate=165,
            calories_burned=650,
        ),
        Workout(
            id=2,
            user_id=user_id,
            duration=timedelta(hours=1, minutes=30),
            moving_time=timedelta(hours=1, minutes=20),
            distance_km=45.0,
            avg_watts=210,
            normalized_power=225.0,
            intensity_factor=0.84,
            training_stress_score=85.0,
            avg_cadence=88,
            avg_speed=33.8,
            avg_speed_without_stop=35,
            avg_heartrate=150,
            max_heartrate=178,
            calories_burned=900,
        ),
        Workout(
            id=3,
            user_id=user_id,
            duration=timedelta(hours=2),
            moving_time=timedelta(hours=1, minutes=50),
            distance_km=70.0,
            avg_watts=160,
            normalized_power=175.0,
            intensity_factor=0.65,
            training_stress_score=60.0,
            avg_cadence=82,
            avg_speed=38.2,
            avg_speed_without_stop=39,
            avg_heartrate=135,
            max_heartrate=160,
            calories_burned=1200,
        ),
        Workout(
            id=4,
            user_id=user_id,
            duration=timedelta(minutes=45),
            moving_time=timedelta(minutes=42),
            distance_km=20.0,
            avg_watts=250,
            normalized_power=270.0,
            intensity_factor=0.95,
            training_stress_score=110.0,
            avg_cadence=92,
            avg_speed=28.6,
            avg_speed_without_stop=29,
            avg_heartrate=165,
            max_heartrate=185,
            calories_burned=550,
        ),
        Workout(
            id=5,
            user_id=user_id,
            duration=timedelta(hours=1, minutes=15),
            moving_time=timedelta(hours=1, minutes=10),
            distance_km=40.0,
            avg_watts=190,
            normalized_power=205.0,
            intensity_factor=0.78,
            training_stress_score=75.0,
            avg_cadence=87,
            avg_speed=34.3,
            avg_speed_without_stop=35,
            avg_heartrate=145,
            max_heartrate=172,
            calories_burned=800,
        ),
    ]
    return result


@pytest.fixture()
def workout_repo(test_workouts) -> FakeWorkoutRepository:
    repo = FakeWorkoutRepository(test_workouts)
    return repo


@pytest.fixture()
def get_fake_statistic_service(workout_repo) -> StatisticsService:
    return StatisticsService(workout_repo=workout_repo)
