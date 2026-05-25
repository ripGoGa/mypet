from sqlmodel import Session, select

from app.models.models import Users


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_email(self, email: str) -> Users:
        user = self.session.exec(select(Users).where(Users.email == email)).first()
        return user

    def add_user(self, user: Users) -> Users:
        self.session.add(user)
        self.session.flush()
        return user
