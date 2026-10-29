from datetime import UTC, datetime, timedelta
from typing import Sequence

from sqlalchemy import func
from sqlmodel import Session, select

from app.models.models import UploadedFile, Workout


class WorkoutRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_one_workout(self, user_id: int, workout_id: int) -> Workout | None:
        workout = self.session.exec(select(Workout).where(Workout.id == workout_id, Workout.user_id == user_id)).first()
        return workout

    def add_uploaded_file(self, uploaded_file: UploadedFile) -> UploadedFile:
        self.session.add(uploaded_file)
        self.session.flush()
        return uploaded_file

    def get_by_hash(self, sha256: str, user_id: int) -> UploadedFile | None:
        existing = self.session.exec(
            select(UploadedFile).where(UploadedFile.sha256 == sha256, UploadedFile.user_id == user_id)
        ).first()
        return existing

    def add_workout(self, workout: Workout) -> Workout:
        self.session.add(workout)
        self.session.flush()
        return workout

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()

    def get_workouts(self, user_id: int, limit: int, offset: int, period: int) -> tuple[Sequence[Workout], int]:
        conditions = [Workout.user_id == user_id]
        if period:
            target_date = datetime.now(UTC) - timedelta(days=period)
            conditions.append(Workout.started_at >= target_date)

        page_query = (
            select(Workout)
            .where(*conditions)
            .order_by(Workout.started_at.desc(), Workout.id.desc())
            .limit(limit)
            .offset(offset)
        )
        count_query = select(func.count()).select_from(Workout).where(*conditions)
        workouts = self.session.exec(page_query).all()
        total = self.session.exec(count_query).one()
        return workouts, total
