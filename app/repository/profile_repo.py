from datetime import date, datetime
from typing import Optional

from sqlmodel import Session

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

    def edit_profile(self, user_profile: UserProfile, athlete_profile: AthleteProfile) -> tuple[UserProfile,AthleteProfile]:
        curr_user_profile = self.get_user_profile(user_profile.id)
        curr_athlete_profile = self.get_athlete_profile(user_profile.id)

        curr_user_profile.sqlmodel_update(user_profile.model_dump(exclude={'id'}))
        curr_athlete_profile.sqlmodel_update(athlete_profile.model_dump(exclude={'id'}))
        self.session.commit()
        return curr_user_profile, curr_athlete_profile

    def get_user_profile(self, user_id: int) -> Optional[UserProfile]:
        return self.session.get(UserProfile, user_id)

    def get_athlete_profile(self, user_id: int) -> Optional[AthleteProfile]:
        return self.session.get(AthleteProfile, user_id)


