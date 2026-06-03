from datetime import date, datetime
from typing import Optional

from sqlmodel import Session

from app.core.exceptions import ProfileAlreadyExistsError
from app.models.models import UserProfile, AthleteProfile


class ProfileRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_user_profile(self, user_profile: UserProfile, athlete_profile: AthleteProfile) -> tuple[UserProfile,
    AthleteProfile]:
        self.session.add(user_profile)
        self.session.add(athlete_profile)
        self.session.commit()
        return user_profile, athlete_profile

    def edit_profile(self, name: str, birth_date: Optional[date], height_cm: Optional[int],
                     updated_at: datetime = datetime.now) -> UserProfile:
        pass

    def check_profile(self, user_id: int) -> Optional[UserProfile]:
        return self.session.get(UserProfile, user_id)


