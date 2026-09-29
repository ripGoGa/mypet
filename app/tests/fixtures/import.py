from typing import List

import pytest

from app.models.models import UploadedFile, Workout
from app.services.import_service import ImportService


class FakeImportWorkoutRepository:
    def __init__(self, dup=None):
        self.uploaded_files = []
        self.workouts = []
        self.commit_calls = 0
        self.rollback_calls = 0
        self.duplicate_file = dup

    def get_by_hash(self, sha256: str, user_id: int) -> bool | None:
        return self.duplicate_file

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
    def __init__(self, filename: str, content: bytes):
        self.filename = filename
        self.content = content

    async def read(self) -> bytes:
        return self.content


@pytest.fixture()
def fake_uploaded_file() -> FakeUploadFile:
    return FakeUploadFile("file.fit", b"")


@pytest.fixture()
def fake_uploaded_files() -> List[FakeUploadFile]:
    return [FakeUploadFile("file.fit", b""), FakeUploadFile("file2.fit", b""), FakeUploadFile("file.csv", b"")]


@pytest.fixture()
def fake_import_repository():
    return FakeImportWorkoutRepository(dup=None)


@pytest.fixture()
def fake_dup_import_repository():
    return FakeImportWorkoutRepository(dup=True)


@pytest.fixture()
def fake_dup_import_service(fake_dup_import_repository):
    return ImportService(fake_dup_import_repository)


@pytest.fixture()
def fake_import_service(fake_import_repository: FakeImportWorkoutRepository):
    return ImportService(workout_repo=fake_import_repository)
