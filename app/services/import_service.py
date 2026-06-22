from fastapi import File
from app.models.models import UploadedFile, Users
from fastapi import File

from app.models.models import UploadedFile
from app.repository.workout_repo import WorkoutRepository
from app.services.file_service import validate_file_type, save_file_with_hash


class ImportService:
    def __init__(self, workout_repo: WorkoutRepository):
        self.workout_repo = workout_repo

    def import_files(self, user: Users, files: list[UploadedFile] = File(...)) -> tuple[int, int, int]:
        success_count = 0
        dup_count = 0
        type_err_count = 0
        for file in files:
            try:
                validate_file_type(filename=file.filename, content_type=file.content_type)
                content = file.read()
                file_path, hash_value = save_file_with_hash(content, )




