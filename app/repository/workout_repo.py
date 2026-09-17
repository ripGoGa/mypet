from datetime import UTC, datetime, timedelta
from typing import Optional, Sequence

from sqlalchemy import desc, func
from sqlmodel import Session, select

from app.models.models import UploadedFile, Workout


class WorkoutRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_one_workout(self, user_id: int, workout_id: int) -> Optional[Workout]:
        workout = self.session.exec(select(Workout).where(Workout.id == workout_id,
                                                          Workout.user_id == user_id)).first()
        return workout

    def add_uploaded_file(self, uploaded_file: UploadedFile) -> UploadedFile:
        self.session.add(uploaded_file)
        self.session.flush()
        return uploaded_file

    def get_by_hash(self, sha256: str, user_id: int) -> Optional[UploadedFile]:
        existing = self.session.exec(
            select(UploadedFile).where(UploadedFile.sha256 == sha256,
                                       UploadedFile.user_id == user_id)).first()
        return existing

    def add_workout(self, workout: Workout) -> Workout:
        self.session.add(workout)
        self.session.flush()
        return workout

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()