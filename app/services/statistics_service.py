from app.repository.cycling_repo import CyclingWorkoutRepository
from app.repository.running_repo import RunningWorkoutRepository
from app.schemas.cycling_dto import CyclingStatsDTO
from app.schemas.running_dto import RunningStatsDTO
from app.services.cycling_stats_calculator import CyclingStatsCalculator
from app.services.running_stats_calculator import RunningStatsCalculator


class StatisticsService:
    def __init__(self, cycling_repo: CyclingWorkoutRepository, running_repo: RunningWorkoutRepository):
        self.cycling_repo = cycling_repo
        self.running_repo = running_repo

    def get_cycling_stats(self, user_id: int, period: int = 0) -> CyclingStatsDTO:
        workouts = self.cycling_repo.get_statistic_workouts(user_id=user_id, period=period)
        statistic = CyclingStatsCalculator(workouts)
        result = CyclingStatsDTO.model_validate(statistic, from_attributes=True)
        return result

    def get_running_stats(self, user_id: int, period: int = 0) -> RunningStatsDTO:
        workouts = self.running_repo.get_statistic_workouts(user_id=user_id, period=period)
        statistic = RunningStatsCalculator(workouts)
        result = RunningStatsDTO.model_validate(statistic, from_attributes=True)
        return result