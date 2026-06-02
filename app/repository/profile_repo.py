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

    def edit_profile(self, name: str, birth_date: Optional[date], height_cm: Optional[int],
                     updated_at: datetime = datetime.now) -> UserProfile:
        pass

    def add_athlete_profile(self, weight_kg: Optional[float], current_ftp: Optional[int], limitations: Optional[str],
                            weekly_hours: Optional[int], gear: Optional[str],
                            environment_location: Optional[str]) -> AthleteProfile:
        pass

    def edit_athlete_profile(self) -> AthleteProfile:
        pass
