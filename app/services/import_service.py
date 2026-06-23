import hashlib
from datetime import datetime, UTC

from fastapi import Depends
from sqlmodel import Session

from app.db.session import get_session
from app.models.models import UploadedFile
from app.models.models import Users
from app.repository.workout_repo import WorkoutRepository
from app.services.file_service import validate_file_type, save_file_with_hash, FileAlreadyExistsError, \
    FileValidationError
from app.services.parse_cvs import parse_csv_to_workout, ParseCsvError


class ImportService:
    def __init__(self, workout_repo: WorkoutRepository, session: Session):
        self.workout_repo = workout_repo
        self.session = session

    async def import_files(self, user: Users, files: list) -> tuple[int, int, int]:
        success_count = 0
        dup_count = 0
        type_err_count = 0
        for file in files:
            try:
                validate_file_type(filename=file.filename, content_type=file.content_type)
                content = await file.read()
                hash_check = hashlib.sha256(content).hexdigest()
                if self.workout_repo.get_by_hash(sha256=hash_check, user_id=user.id):
                    raise FileAlreadyExistsError
                file_path, hash_value = save_file_with_hash(content)
                uploaded_file = UploadedFile(original_name=file.filename, sha256=hash_value, uploaded_at=datetime.now(UTC),
                                             user_id=user.id)
                self.workout_repo.add_uploaded_file(uploaded_file)
                parse_csv_to_workout(file_path=file_path, uf_id=uploaded_file.id, session=self.session, user_id=user.id)
                success_count += 1
                self.session.commit()
            except ParseCsvError:
                self.session.rollback()
                type_err_count += 1
            except FileValidationError:
                self.session.rollback()
                type_err_count += 1
            except FileAlreadyExistsError:
                self.session.rollback()
                dup_count += 1
            except OSError:
                self.session.rollback()
                type_err_count += 1

            except Exception as e:
                self.session.rollback()
                type_err_count += 1
                print(f"Неизвестная ошибка при загрузке {file.filename}: {e}")  # Для дебага в консоли
        return success_count, dup_count, type_err_count


def get_import_service(session: Session = Depends(get_session)) -> ImportService:
    repo = WorkoutRepository(session=session)
    new_import_service = ImportService(workout_repo=repo, session=session)
    return new_import_service



