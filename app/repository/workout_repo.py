from datetime import datetime, timedelta, UTC
from math import ceil
from typing import Optional, Tuple, Sequence, Any

from sqlalchemy import func, desc
from sqlmodel import Session, select
from app.models.models import Users, Workout, UploadedFile


class WorkoutRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_workouts(self, user_id: int, period: int, limit: int, offset: int) -> tuple[Sequence[Workout], int]:
        # 1. Чистый запрос
        query_workouts = select(Workout).where(Workout.user_id == user_id)
        query_count = select(func.count(Workout.id)).where(Workout.user_id == user_id)
        # 2. Формируем запрос из роута статистики
        if period:
            target_date = datetime.now(UTC) - timedelta(days=period)
            query_workouts = query_workouts.join(UploadedFile).where(UploadedFile.uploaded_at >= target_date)
            query_count = query_count.join(UploadedFile).where(UploadedFile.uploaded_at >= target_date)
        # 3. Формируем запрос для простого просмотра тренировок
        query_workouts = (query_workouts.order_by(desc(Workout.id)).limit(limit).offset(offset))
        # 4. Делаем запрос в базу
        workouts = self.session.exec(query_workouts).all()
        total_count = self.session.exec(query_count).one()
        return workouts, total_count

    def get_one_workout(self, user_id: int, workout_id: int) -> Optional[Workout]:
        workout = self.session.exec(select(Workout).where(Workout.id == workout_id,
                                                          Workout.user_id == user_id)).first()
        return workout
