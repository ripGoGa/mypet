import hashlib
from datetime import UTC, datetime

from app.core.exceptions import ParseFitError
from app.models import CyclingWorkout
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
from app.services.fit_cycling_parse import parse_fit_cycling
from app.services.read_fit_file import read_fit_file

PARSERS = {"cycling": parse_fit_cycling}
MODELS = {"cycling": CyclingWorkout}


class ImportService:
    def __init__(self, workout_repo: WorkoutRepository, profile_repo: ProfileRepository):
        self.workout_repo = workout_repo
        self.profile_repo = profile_repo

    async def import_files(self, user: Users, files: list) -> tuple[int, int, int]:
        success_count = 0
        dup_count = 0
        type_err_count = 0
        for file in files:
            file_path = None
            try:
                validate_file_type(filename=file.filename)
                content = await file.read()
                hash_check = hashlib.sha256(content).hexdigest()
                if self.workout_repo.get_by_hash(sha256=hash_check, user_id=user.id):
                    raise FileAlreadyExistsError
                file_path, hash_value = save_file_with_hash(content)
                uploaded_file = UploadedFile(
                    original_name=file.filename,
                    sha256=hash_value,
                    uploaded_at=datetime.now(UTC),
                    user_id=user.id,
                )
                self.workout_repo.add_uploaded_file(uploaded_file)
                session_dict, sport = read_fit_file(file_path=file_path)
                workout, sport_dict = PARSERS[sport](
                    session_dict=session_dict, user_id=user.id, uploaded_file_id=uploaded_file.id
                )
                self.workout_repo.add_workout(workout)
                sport_workout = MODELS[sport](workout_id=workout.id, **sport_dict)
                self.workout_repo.add_workout(sport_workout)

                self.workout_repo.commit()
                success_count += 1
            except ParseFitError:
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
