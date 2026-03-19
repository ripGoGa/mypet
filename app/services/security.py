import copy
import datetime

import jwt
from passlib.context import CryptContext

SECRET_KEY = 'Mysecretkey2131jbvadjladvbcvabaljfghdvbcnxcnmbvxcnmxbvxmbnvc'
ALGORITHM = 'HS256'

my_cc = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_password_hash(password: str) -> str:
    hash_password = my_cc.hash(password)
    return hash_password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    result = my_cc.verify(plain_password, hashed_password)
    return result


def create_access_token(data: dict) -> str:
    # Время жизни токена
    exp = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=30)
    # Создаем словарь для токена
    to_encode = data.copy()
    to_encode['exp'] = exp
    # Создание токена
    jwt_token = jwt.encode(payload=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    return jwt_token
