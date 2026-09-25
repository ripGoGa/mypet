import hashlib
from pathlib import Path


class FileValidationError(Exception):
    """Выбрасывается когда тип файла не подходит"""

    pass


class FileAlreadyExistsError(Exception):
    """Файл с таким содержимым уже существует"""

    pass


def validate_file_type(filename: str) -> None:
    if filename.lower().endswith(".fit"):
        pass
    else:
        raise FileValidationError("Можно загружать только FIT-файлы!")


def save_file_with_hash(content: bytes) -> tuple[str, str]:
    hash_value = hashlib.sha256(content).hexdigest()
    filename = f"{hash_value}.csv"
    path = Path("data/csv") / f"{filename}"
    try:
        path.write_bytes(content)
    except OSError as e:
        delete_file(str(path))
        raise OSError(f"Не удалось сохранить файл: {e}") from e

    return str(path), hash_value


def delete_file(filepath: str) -> None:
    Path(filepath).unlink(missing_ok=True)
