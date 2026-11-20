from dataclasses import dataclass
from math import ceil
from typing import Sequence

from pydantic import ValidationError

from app.core.exceptions import CorruptedDataError, MissingWorkoutError
from app.models import CyclingWorkout
from app.models.models import Workout
from app.repository.cycling_repo import CyclingWorkoutRepository
from app.repository.running_repo import RunningWorkoutRepository
from app.repository.workout_repo import WorkoutRepository
from app.schemas.cycling_workout_detail_dto import CyclingWorkoutDetailDTO
from app.schemas.running_workout_detail_dto import RunningWorkoutDetailDTO


@dataclass(frozen=True)
class SportHandlers:
    repo: CyclingWorkoutRepository | RunningWorkoutRepository
    dto_class: type[RunningWorkoutDetailDTO | CyclingWorkoutDetailDTO]


class WorkoutService:
    def __init__(
        self,
        work_repo: WorkoutRepository,
        cycling_repo: CyclingWorkoutRepository,
        running_repo: RunningWorkoutRepository,
    ):
        self.workout_repo = work_repo
        self.sport_dict = {
            "cycling": SportHandlers(repo=cycling_repo, dto_class=CyclingWorkoutDetailDTO),
            "running": SportHandlers(repo=running_repo, dto_class=RunningWorkoutDetailDTO),
        }

    def get_user_workouts(
        self, user_id: int, page: int, limit: int, period: int
    ) -> tuple[Sequence[tuple[Workout, CyclingWorkout]], int]:
        """ожидает page >= 1, 1 <= limit <= 100, period >= 0, проверка на корректность происходит в роуте"""
        offset = (page - 1) * limit
        workouts, total_count = self.sport_dict["cycling"].repo.get_workouts(
            user_id=user_id, period=period, limit=limit, offset=offset
        )
        total_pages = ceil(total_count / limit)
        return workouts, total_pages

    def get_user_workout(self, workout_id: int, user_id: int) -> RunningWorkoutDetailDTO | CyclingWorkoutDetailDTO:
        workout = self.workout_repo.get_one_workout(user_id=user_id, workout_id=workout_id)
        if workout is None:
            raise MissingWorkoutError(workout_id, user_id)
        if workout.sport not in self.sport_dict:
            raise CorruptedDataError(workout_id, user_id, workout.sport)
        handlers = self.sport_dict[workout.sport]
        sport_workout = handlers.repo.get_by_workout_id(workout_id=workout_id, user_id=user_id)
        if sport_workout is None:
            raise CorruptedDataError(workout_id, user_id, "sport_workout_is_none")
        try:
            dto = handlers.dto_class.from_models(workout, sport_workout)

        except ValidationError as e:
            raise CorruptedDataError(workout_id, user_id, "error_in_dto_creation") from e
        return dto
