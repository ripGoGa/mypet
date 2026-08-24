import pytest

from app.services.file_service import FileValidationError
from app.services.parse_cvs import ParseCsvError


@pytest.mark.asyncio
async def test_import_files_success(monkeypatch, test_workouts, fake_import_service, fake_csv_file,
                              test_user, fake_import_repository):
    test_workout = test_workouts[0]

    def fake_parse_csv_to_workout(file_path, user_id, uf_id, ftp):
        return test_workout

    def fake_validate_file_type(filename: str, content_type: str) -> None:
        pass

    def fake_save_file_with_hash(content:bytes) -> tuple[str, str]:
        return ('c/ride.csv', 'fhakfjkashjfa')

    monkeypatch.setattr('app.services.import_service.parse_csv_to_workout', fake_parse_csv_to_workout)
    monkeypatch.setattr("app.services.import_service.validate_file_type", fake_validate_file_type)
    monkeypatch.setattr("app.services.import_service.save_file_with_hash", fake_save_file_with_hash)
    result = await fake_import_service.import_files(test_user, [fake_csv_file])
    assert result == (1, 0, 0)
    assert len(fake_import_repository.uploaded_files) == 1
    assert len(fake_import_repository.workouts) == 1
    assert fake_import_repository.commit_calls == 1
    assert fake_import_repository.rollback_calls == 0

@pytest.mark.asyncio
async def test_import_files_duplicate(monkeypatch, fake_csv_file, test_user,
                                      fake_dup_import_repository, fake_dup_import_service):
    def fake_validate_file_type(filename: str, content_type: str) -> None:
        pass

    monkeypatch.setattr("app.services.import_service.validate_file_type", fake_validate_file_type)
    result = await fake_dup_import_service.import_files(test_user, [fake_csv_file])
    assert result == (0, 1, 0)
    assert len(fake_dup_import_repository.uploaded_files) == 0
    assert len(fake_dup_import_repository.workouts) == 0
    assert fake_dup_import_repository.commit_calls == 0
    assert fake_dup_import_repository.rollback_calls == 1


@pytest.mark.asyncio
async def test_import_files_validate_error(monkeypatch, test_user, fake_import_repository,
                                           fake_import_service, fake_csv_file):
    def fake_validate_file_type(filename: str, content_type: str) -> None:
        raise FileValidationError('Можно загружать только CSV-файлы!')

    monkeypatch.setattr("app.services.import_service.validate_file_type", fake_validate_file_type)
    result = await fake_import_service.import_files(test_user, [fake_csv_file])
    assert result == (0, 0, 1)
    assert len(fake_import_repository.uploaded_files) == 0
    assert len(fake_import_repository.workouts) == 0
    assert fake_import_repository.commit_calls == 0
    assert fake_import_repository.rollback_calls == 1


@pytest.mark.asyncio
async def test_import_files_parse_error(monkeypatch, fake_import_service, fake_csv_file,
                              test_user, fake_import_repository):

    def fake_parse_csv_to_workout(file_path, user_id, uf_id, ftp):
        raise ParseCsvError

    def fake_validate_file_type(filename: str, content_type: str) -> None:
        pass

    def fake_save_file_with_hash(content:bytes) -> tuple[str, str]:
        return ('c/ride.csv', 'fhakfjkashjfa')

    monkeypatch.setattr('app.services.import_service.parse_csv_to_workout', fake_parse_csv_to_workout)
    monkeypatch.setattr("app.services.import_service.validate_file_type", fake_validate_file_type)
    monkeypatch.setattr("app.services.import_service.save_file_with_hash", fake_save_file_with_hash)
    result = await fake_import_service.import_files(test_user, [fake_csv_file])
    assert result == (0, 0, 1)
    assert len(fake_import_repository.uploaded_files) == 1
    assert len(fake_import_repository.workouts) == 0
    assert fake_import_repository.commit_calls == 0
    assert fake_import_repository.rollback_calls == 1


@pytest.mark.asyncio
async def test_import_files_os_error(monkeypatch, fake_import_service, fake_csv_file,
                              test_user, fake_import_repository):

    def fake_validate_file_type(filename: str, content_type: str) -> None:
        pass

    def fake_save_file_with_hash(content:bytes) -> tuple[str, str]:
        raise OSError

    monkeypatch.setattr("app.services.import_service.validate_file_type", fake_validate_file_type)
    monkeypatch.setattr("app.services.import_service.save_file_with_hash", fake_save_file_with_hash)
    result = await fake_import_service.import_files(test_user, [fake_csv_file])
    assert result == (0, 0, 1)
    assert len(fake_import_repository.uploaded_files) == 0
    assert len(fake_import_repository.workouts) == 0
    assert fake_import_repository.commit_calls == 0
    assert fake_import_repository.rollback_calls == 1