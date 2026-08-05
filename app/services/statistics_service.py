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

