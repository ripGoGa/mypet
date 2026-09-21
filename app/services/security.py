import datetime

import bcrypt
import jwt
from app.core.config import key_settings

SECRET_KEY = key_settings.secret_key
ALGORITHM = 'HS256'



def get_password_hash(password: str) -> str:
    hash_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    return hash_password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(data: dict) -> str:
    # Время жизни токена
    exp = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=30)
    # Создаем словарь для токена
    to_encode = data.copy()
    to_encode['exp'] = exp
    # Создание токена
    jwt_token = jwt.encode(payload=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    return jwt_token
