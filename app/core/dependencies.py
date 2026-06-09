import jwt
from app.db.session import get_session
from fastapi import Depends, HTTPException
from app.models.models import Users
from starlette.requests import Request
from sqlmodel import select
from app.services.security import SECRET_KEY, ALGORITHM


def get_current_user(request: Request, session=Depends(get_session)):
    """"Проверяет токен на соответствие"""
    token = request.cookies.get('access_token')
    if not token:
        raise HTTPException(status_code=401, detail='Ошибка авторизации')
    try:
        # Пробует декодировать подпись токена с помощью секретного ключа
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user = session.exec(select(Users).where(Users.email == payload['sub'])).first()
        if not user:
            raise HTTPException(status_code=401, detail='Ошибка авторизации')
        return user
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail='Ошибка авторизации')
