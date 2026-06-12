import os
import shutil
import pytest
from sqlmodel import Session, create_engine
from app.main import app
from app.db.session import get_session
from fastapi.testclient import TestClient

ORIGINAL_DB_PATH = "app/data/app.db"
TEST_DB_PATH = "app/data/test_app.db"
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
    client.post('/register', data={'email': 'test_client@ya.ru', 'password': 'secure_pass'})
    client.post('/login', data={'username': 'test_client@ya.ru', 'password': 'secure_pass'})
    client
    yield client


@pytest.fixture()
def db_test_session():
    with Session(test_engine) as session:
        yield session
