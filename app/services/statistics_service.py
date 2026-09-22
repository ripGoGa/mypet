from app.repository.cycling_repo import CyclingWorkoutRepository
from app.repository.workout_repo import WorkoutRepository
from app.schemas.workoutDTO import WorkoutsDTO
from app.services.cycling_stats_calculator import CyclingStatsCalculator


class StatisticsService:
    def __init__(self, workout_repo: WorkoutRepository, cycling_repo: CyclingWorkoutRepository):
        self.workout_repo = workout_repo
        self.cycling_repo = cycling_repo

    def get_user_stats(self, user_id: int, period: int = 0) -> WorkoutsDTO:
        workouts = self.cycling_repo.get_statistic_workouts(user_id=user_id, period=period)
        statistic = CyclingStatsCalculator(workouts)
        result = WorkoutsDTO.model_validate(statistic, from_attributes=True)
        return result

