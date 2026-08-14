from pathlib import Path

import jwt
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from sqlmodel import select
from starlette.requests import Request

from app.core.dependencies import get_current_user
from app.core.templating import templates
from app.db.session import create_db_and_tables, get_session
from app.models.models import Users
from app.routers import chat, coach, imports, login, profile, register, statistics, workout
from app.services.security import ALGORITHM, SECRET_KEY

app = FastAPI(title="Bike Tracker")

app.include_router(login.router)
app.include_router(register.router)
app.include_router(profile.router)
app.include_router(workout.router)
app.include_router(statistics.router)
app.include_router(imports.router)
app.include_router(chat.router)
app.include_router(coach.router)


def on_startup() -> None:
    create_db_and_tables()


def ensure_data_store() -> None:
    Path('data/csv').mkdir(parents=True, exist_ok=True)


on_startup()
ensure_data_store()


@app.get('/', response_class=HTMLResponse)
async def hello_root(request: Request, session=Depends(get_session)):
    # Пытаемся узнать имя пользователя для приветствия
    token = request.cookies.get('access_token')
    user_profile = None
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user = session.exec(select(Users).where(Users.email == payload['sub'])).first()
            user_profile = user.user_profile if user else None
        except jwt.InvalidTokenError:
            pass

    return templates.TemplateResponse(request, 'index.html', {'user_profile': user_profile})


@app.get('/me')
def me(user=Depends(get_current_user)) -> dict:
    return {'id': user.id, 'email': user.email}


@app.exception_handler(HTTPException)
def error(request: Request, exc: HTTPException):
    status_code = exc.status_code
    detail = exc.detail
    return templates.TemplateResponse(request, 'error.html', {'detail': detail, 'status_code': status_code},
                                      status_code=status_code)
