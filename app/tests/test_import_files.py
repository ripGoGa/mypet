import pytest


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
