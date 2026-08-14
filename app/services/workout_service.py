from math import ceil
from typing import Optional, Sequence

from app.core.exceptions import MissingWorkoutError
from app.db.session import get_session
from app.models.models import Workout
from app.repository.workout_repo import WorkoutRepository
from fastapi import Depends
from sqlmodel import Session


class WorkoutService:
    def __init__(self, work_repo: WorkoutRepository):
        self.workout_repo = work_repo

    def get_user_workouts(self, user_id: int, page: int, limit: int, period: int) -> tuple[Sequence[Workout], int]:
        if page < 1:
            page = 1
        if limit > 100 or limit < 1:
            limit = 10
        offset = (page - 1) * limit
        workouts, total_count = self.workout_repo.get_workouts(user_id=user_id, period=period,
                                                               limit=limit, offset=offset
                                                               )
        total_pages = ceil(total_count / limit)
        return workouts, total_pages

    def get_user_workout(self, workout_id: int, user_id: int) -> Workout:
        workout = self.workout_repo.get_one_workout(user_id=user_id, workout_id=workout_id)
        if workout:
            return workout
        raise MissingWorkoutError

