import hashlib
import datetime
from pathlib import Path
from sqlmodel import select, Session
from app.models.models import UploadedFile


class FileValidationError(Exception):
    """Выбрасывается когда тип файла не подходит"""
    pass


class FileAlreadyExistsError(Exception):
    """Файл с таким содержимым уже существует"""
    pass


def validate_file_type(filename: str, content_type: str) -> None:
    ct = (content_type or '').lower()
    allowed_ct = {'text/csv'}
    if filename.lower().endswith('.csv') and ct in allowed_ct:
        pass
    else:
        raise FileValidationError('Можно загружать только CSV-файлы!')


def save_file_with_hash(content: bytes, session: Session) -> tuple[str, str]:
    hash_value = hashlib.sha256(content).hexdigest()
    filename = f"{hash_value}.csv"
    path = Path('data/csv') / f'{filename}'
    existing = session.exec(select(UploadedFile).where((UploadedFile.sha256 == hash_value))).first()
    if existing:
        raise FileAlreadyExistsError('Файл с таким содержимым уже существует')
    try:
        path.write_bytes(content)
    except (PermissionError, OSError) as e:
        raise OSError(f"Не удалось сохранить файл: {e}")
    return str(path), hash_value
