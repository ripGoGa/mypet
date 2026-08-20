from typing import Optional

import pytest

from app.models.models import AthleteProfile, UploadedFile, Workout
from app.services.import_service import ImportService


class FakeProfileRepository:
    def __init__(self, athlete_profile: AthleteProfile):
        self.athlete_profile = athlete_profile

    def get_athlete_profile(self, user_id: int) -> Optional[AthleteProfile]:
        return self.athlete_profile


class FakeImportWorkoutRepository:
    def __init__(self):
        self.uploaded_files = []
        self.workouts = []
        self.commit_calls = 0
        self.rollback_calls = 0

    def get_by_hash(self, sha256: str, user_id: int) -> None:
        return None

    def add_uploaded_file(self, uploaded_file: UploadedFile) -> UploadedFile:
        uploaded_file.id = 1
        self.uploaded_files.append(uploaded_file)
        return uploaded_file

    def add_workout(self, workout: Workout) -> Workout:
        self.workouts.append(workout)
        return workout

    def commit(self) -> None:
        self.commit_calls += 1

    def rollback(self) -> None:
        self.rollback_calls += 1


class FakeUploadFile:
    def __init__(self, filename: str, content_type: str, content: bytes):
        self.filename = filename
        self.content_type = content_type
        self.content = content

    async def read(self) -> bytes:
        return self.content


@pytest.fixture()
def fake_csv_file() -> FakeUploadFile:
    return FakeUploadFile(filename='ride.csv', content_type='text/csv', content=b'test csv content')


@pytest.fixture()
def fake_profile_repo(load_athlete_profile: AthleteProfile) -> FakeProfileRepository:
    return FakeProfileRepository(load_athlete_profile)


@pytest.fixture()
def fake_import_repository():
    return FakeImportWorkoutRepository()


@pytest.fixture()
def fake_import_service(fake_profile_repo: FakeProfileRepository, fake_import_repository: FakeImportWorkoutRepository):
    return ImportService(workout_repo=fake_import_repository, profile_repo=fake_profile_repo)

