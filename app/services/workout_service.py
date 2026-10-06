from math import ceil
from typing import Sequence

from app.core.exceptions import MissingWorkoutError
from app.models import CyclingWorkout
from app.models.models import Workout
from app.repository.cycling_repo import CyclingWorkoutRepository
from app.repository.workout_repo import WorkoutRepository


class WorkoutService:
    def __init__(self, work_repo: WorkoutRepository, cycling_repo: CyclingWorkoutRepository):
        self.workout_repo = work_repo
        self.cycling_repo = cycling_repo

    def get_user_workouts(
        self, user_id: int, page: int, limit: int, period: int
    ) -> tuple[Sequence[tuple[Workout, CyclingWorkout]], int]:
        """ожидает page >= 1, 1 <= limit <= 100, period >= 0, проверка на корректность происходит в роуте"""
        offset = (page - 1) * limit
        workouts, total_count = self.cycling_repo.get_workouts(
            user_id=user_id, period=period, limit=limit, offset=offset
        )
        total_pages = ceil(total_count / limit)
        return workouts, total_pages

    def get_user_workout(self, workout_id: int, user_id: int) -> Workout:
        workout = self.workout_repo.get_one_workout(user_id=user_id, workout_id=workout_id)
        if workout:
            return workout
        raise MissingWorkoutError
