from datetime import UTC, datetime, timedelta
from typing import Sequence

from sqlalchemy import desc, func
from sqlmodel import Session, select

from app.models.models import Workout
from app.models.training_models import CyclingWorkout


class CyclingWorkoutRepository:
    def __init__(self, session: Session):
        self.session = session


    def get_workouts(self, user_id: int, period: int, limit: int, offset: int) -> tuple[
        Sequence[tuple[Workout, CyclingWorkout]], int]:
        # 1. Чистый запрос (join + user_id)
        query_workouts = (
            select(Workout, CyclingWorkout)
            .where(Workout.user_id == user_id)
            .join(CyclingWorkout, CyclingWorkout.workout_id == Workout.id)
        )

        # 2. Фильтр по периоду
        if period:
            target_date = datetime.now(UTC) - timedelta(days=period)
            query_workouts = query_workouts.where(Workout.started_at >= target_date)

        # 3. Считаем total_count по уже отфильтрованному запросу
        total_count = self.session.exec(select(func.count()).select_from(query_workouts.subquery())).one()

        # 4. Сортировка и пагинация
        query_workouts = (query_workouts.order_by(desc(Workout.id)).limit(limit).offset(offset))

        # 5. Делаем запрос в базу
        workouts = self.session.exec(query_workouts).all()
        
        return workouts, total_count

    def get_statistic_workouts(self, user_id: int, period: int = 0) -> Sequence[tuple[Workout, CyclingWorkout]]:
        # 1. Чистый запрос
        query_workouts = (select(Workout, CyclingWorkout)
                          .where(Workout.user_id == user_id)
                          .join(CyclingWorkout, CyclingWorkout.workout_id == Workout.id))
        if period:
            target_date = datetime.now(UTC) - timedelta(days=period)
            query_workouts = query_workouts.where(Workout.started_at >= target_date)
        result = self.session.exec(query_workouts).all()
        return result


