from fastapi import Depends
from sqlmodel import Session

from app.db.session import get_session
from app.repository.workout_repo import WorkoutRepository
from app.schemas.workoutDTO import WorkoutsDTO
from app.services.stats_calculator import StatsCalculator


class StatisticsService:
    def __init__(self, workout_repo: WorkoutRepository):
        self.workout_repo = workout_repo

    def get_user_stats(self, user_id: int, period: int = 0) -> WorkoutsDTO:
        workouts = self.workout_repo.get_statistic_workouts(user_id=user_id, period=period)
        statistic = StatsCalculator(workouts)
        result = WorkoutsDTO.model_validate(statistic, from_attributes=True)
        return result


def get_statistics_service(session: Session = Depends(get_session)) -> StatisticsService:
    repo = WorkoutRepository(session=session)
    new_statistics_service = StatisticsService(workout_repo=repo)
    return new_statistics_service
