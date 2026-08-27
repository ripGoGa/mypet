from app.core.exceptions import ProfileAlreadyExistsError
from app.models.models import AthleteProfile, UserProfile
from app.repository.profile_repo import ProfileRepository
from app.schemas.profile import ProfileCreateDTO


class ProfileService:
    def __init__(self, profile_repo: ProfileRepository):
        self.profile_repo = profile_repo

    def create_new_profile(self, user_data: ProfileCreateDTO, user_id: int) -> tuple[UserProfile, AthleteProfile]:
        if self.profile_repo.get_user_profile(user_id):
            raise ProfileAlreadyExistsError
        user_profile = UserProfile(id=user_id, name=user_data.name, birth_date=user_data.birth_date,
                                   height_cm=user_data.height_cm)
        athlete_profile = AthleteProfile(id=user_id, weight_kg=user_data.weight_kg, current_ftp=user_data.current_ftp,
                                         gear=user_data.gear, environment_location=user_data.environment_location,
                                         limitations=user_data.limitations,
                                         weekly_hours=user_data.weekly_hours)
        result = self.profile_repo.add_user_profile(user_profile=user_profile, athlete_profile=athlete_profile)
        return result

    def edit_profile(self, user_data: ProfileCreateDTO, user_id: int) -> tuple[UserProfile, AthleteProfile]:
        user_profile = UserProfile(id=user_id, name=user_data.name, birth_date=user_data.birth_date,
                                   height_cm=user_data.height_cm)
        athlete_profile = AthleteProfile(id=user_id, weight_kg=user_data.weight_kg, current_ftp=user_data.current_ftp,
                                         gear=user_data.gear, environment_location=user_data.environment_location,
                                         limitations=user_data.limitations,
                                         weekly_hours=user_data.weekly_hours)
        result = self.profile_repo.edit_profile(user_profile=user_profile, athlete_profile=athlete_profile)
        return result

