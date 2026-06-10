from fastapi import Depends
from sqlmodel import Session

from app.core.exceptions import UserAlreadyExistError, UserEmailPasswordError
from app.db.session import get_session
from app.models.models import Users
from app.repository.user_repo import UserRepository
from app.services.security import get_password_hash, verify_password


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def register_new_user(self, email: str, password: str):
        if self.user_repo.get_by_email(email):
            raise UserAlreadyExistError
        hashed_pas = get_password_hash(password)
        new_user = Users(email=email, hashed_password=hashed_pas)
        self.user_repo.add_user(new_user)

    def authenticate_user(self, email: str, password: str):
        # Looking for a user in the db or raise an exp
        user = self.user_repo.get_by_email(email)
        if not user:
            raise UserEmailPasswordError
        # Verify user and return Users obj
        if verify_password(plain_password=password, hashed_password=user.hashed_password):
            return user
        raise UserEmailPasswordError


def get_user_service(session: Session = Depends(get_session)) -> UserService:
    repo = UserRepository(session=session)
    new_user_service = UserService(user_repo=repo)
    return new_user_service
