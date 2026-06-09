from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)


@pytest.mark.parametrize('email, password', [
    ("user1@gmail.com", "pass123"),
    ("runner_99@ya.ru", "secure_pass"),
    ("olymp@coach.com", "my_secret_key"), ])
def test_registration(email, password):
    response = client.post('/register', data={'email': email, 'password': password},
                           follow_redirects=False)
    assert response.status_code == 303


def test_successful_login():
    client.post('/register', data={'email': 'runner_99@ya.ru', 'password': 'secure_pass'},
                follow_redirects=False)
    response = client.post('/login', data={'username': 'runner_99@ya.ru', 'password': 'secure_pass'},
                           follow_redirects=False)
    assert response.status_code == 303
    assert 'access_token' in response.cookies


def test_unsuccessful_login():
    client.post('/register', data={'email': 'runner_99@ya.ru', 'password': 'secure_pass'},
                follow_redirects=False)
    response = client.post('/login', data={'username': 'runner_99@ya.ru', 'password': 'secure_pas'},
                           follow_redirects=False)
    assert response.status_code == 400
    assert 'access_token' not in response.cookies
