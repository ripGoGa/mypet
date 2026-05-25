from fastapi import HTTPException, Depends
from sqlmodel import Session

from app.db.session import get_session
from app.models.models import Users
from app.repository.user_repo import UserRepository
from app.services.security import get_password_hash


class UserService:
    def __init__(self, user_repo: UserRepository, session: Session):
        self.user_repo = user_repo
        self.session = session

    def register_new_user(self, email: str, password: str) -> Users:
        if self.user_repo.get_by_email(email):
            raise HTTPException(status_code=400, detail='Этот email уже зарегистрирован')
        hashed_pas = get_password_hash(password)
        new_user = Users(email=email, hashed_password=hashed_pas)
        self.user_repo.add_user(new_user)
        self.session.commit()


def get_user_service(session: Session = Depends(get_session)) -> UserService:
    repo = UserRepository(session=session)
    new_user_service = UserService(session=session,user_repo=repo)
    return new_user_service
