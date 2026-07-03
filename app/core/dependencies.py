import jwt
from fastapi import Depends, HTTPException
from sqlmodel import select, Session
from starlette.requests import Request

from app.db.session import get_session
from app.infrastructure.llm.ollama_provider import OllamaProvider
from app.models.models import Users
from app.repository.chat_repo import ChatRepository
from app.repository.profile_repo import ProfileRepository
from app.repository.user_repo import UserRepository
from app.repository.workout_repo import WorkoutRepository
from app.services.coach_service import CoachService
from app.services.import_service import ImportService
from app.services.profile_service import ProfileService
from app.services.security import SECRET_KEY, ALGORITHM
from app.services.statistics_service import StatisticsService
from app.services.user_service import UserService
from app.services.workout_service import WorkoutService


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


def get_chat_repo(session: Session = Depends(get_session)) -> ChatRepository:
    new_chat_repo = ChatRepository(session=session)
    return new_chat_repo


def get_coach_service(session: Session = Depends()) -> CoachService:
    workout_repo = WorkoutRepository(session=session)
    chat_repo = ChatRepository(session=session)
    llm_provider = OllamaProvider()
    new_coach_service = CoachService(workout_repo=workout_repo, chat_repo=chat_repo, llm_provider=llm_provider)
    return new_coach_service


def get_import_service(session: Session = Depends(get_session)) -> ImportService:
    repo = WorkoutRepository(session=session)
    new_import_service = ImportService(workout_repo=repo, session=session)
    return new_import_service


def get_profile_service(session: Session = Depends(get_session)) -> ProfileService:
    repo = ProfileRepository(session=session)
    new_profile_service = ProfileService(profile_repo=repo)
    return new_profile_service


def get_statistics_service(session: Session = Depends(get_session)) -> StatisticsService:
    repo = WorkoutRepository(session=session)
    new_statistics_service = StatisticsService(workout_repo=repo)
    return new_statistics_service


def get_user_service(session: Session = Depends(get_session)) -> UserService:
    repo = UserRepository(session=session)
    new_user_service = UserService(user_repo=repo)
    return new_user_service


def get_workout_service(session: Session = Depends(get_session)) -> WorkoutService:
    repo = WorkoutRepository(session=session)
    new_work_service = WorkoutService(work_repo=repo)
    return new_work_service
