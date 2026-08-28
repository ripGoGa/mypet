import hashlib
from datetime import UTC, datetime

from app.models.models import UploadedFile, Users
from app.repository.profile_repo import ProfileRepository
from app.repository.workout_repo import WorkoutRepository
from app.services.file_service import (
    FileAlreadyExistsError,
    FileValidationError,
    delete_file,
    save_file_with_hash,
    validate_file_type,
)
from app.services.parse_cvs import ParseCsvError, parse_csv_to_workout


class ImportService:
    def __init__(self, workout_repo: WorkoutRepository, profile_repo: ProfileRepository):
        self.workout_repo = workout_repo
        self.profile_repo = profile_repo

    async def import_files(self, user: Users, files: list) -> tuple[int, int, int]:
        success_count = 0
        dup_count = 0
        type_err_count = 0
        athlete_profile = self.profile_repo.get_athlete_profile(user_id=user.id)
        ftp = athlete_profile.current_ftp if athlete_profile else None
        for file in files:
            file_path = None
            try:
                validate_file_type(filename=file.filename, content_type=file.content_type)
                content = await file.read()
                hash_check = hashlib.sha256(content).hexdigest()
                if self.workout_repo.get_by_hash(sha256=hash_check, user_id=user.id):
                    raise FileAlreadyExistsError
                file_path, hash_value = save_file_with_hash(content)
                uploaded_file = UploadedFile(original_name=file.filename, sha256=hash_value,
                                             uploaded_at=datetime.now(UTC),
                                             user_id=user.id)
                self.workout_repo.add_uploaded_file(uploaded_file)
                workout = parse_csv_to_workout(file_path=file_path, uf_id=uploaded_file.id, ftp=ftp,
                                     user_id=user.id)
                self.workout_repo.add_workout(workout)
                self.workout_repo.commit()
                success_count += 1
            except ParseCsvError:
                self.workout_repo.rollback()
                type_err_count += 1
                if file_path:
                    delete_file(file_path=file_path)
            except FileValidationError:
                self.workout_repo.rollback()
                type_err_count += 1
            except FileAlreadyExistsError:
                self.workout_repo.rollback()
                dup_count += 1
            except OSError:
                self.workout_repo.rollback()
                type_err_count += 1
                if file_path:
                    delete_file(file_path=file_path)

            except Exception as e:
                self.workout_repo.rollback()
                type_err_count += 1
                print(f"Неизвестная ошибка при загрузке {file.filename}: {e}")  # Для дебага в консоли
                if file_path:
                    delete_file(file_path=file_path)
        return success_count, dup_count, type_err_count






