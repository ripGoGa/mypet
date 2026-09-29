from datetime import datetime

import fitparse
import pytest
from pandas.errors import EmptyDataError

from app.core.exceptions import ParseFitError
from app.services.file_service import FileValidationError
from app.services.parse_csv import ParseCsvError, parse_csv_to_workout


@pytest.mark.asyncio
async def test_import_files_success(
    monkeypatch, fake_import_service, test_user, fake_import_repository, fake_uploaded_file
):

    def fake_read_fit_file(file_path: str) -> tuple[dict, str]:
        cycling_dict = {
            "timestamp": datetime(2025, 10, 8, 11, 27, 31),
            "start_time": datetime(2025, 10, 8, 10, 20, 52),
            "total_elapsed_time": 3999.0,
            "total_timer_time": 3771.0,
            "total_distance": 37146.43,
            "total_work": 810813,
            "total_moving_time": 3771.0,
            "total_calories": 819,
            "enhanced_avg_speed": 9.85,
            "avg_speed": 9.85,
            "enhanced_max_speed": 16.377,
            "max_speed": 16.377,
            "avg_power": 215,
            "max_power": 930,
            "total_ascent": 287,
            "total_descent": 293,
            "num_laps": 1,
            "normalized_power": 230,
            "training_stress_score": 93.8,
            "intensity_factor": 0.95,
            "left_right_balance": 50,
            "threshold_power": 242,
            "enhanced_avg_altitude": 185.60000000000002,
            "avg_altitude": 185.60000000000002,
            "enhanced_max_altitude": 237.20000000000005,
            "max_altitude": 237.20000000000005,
            "avg_grade": 0.37,
            "sport": "cycling",
            "sub_sport": 252,
            "avg_heart_rate": 159,
            "max_heart_rate": 180,
            "avg_cadence": 87,
            "max_cadence": 115,
            "avg_temperature": 17,
            "max_temperature": 22,
        }
        return cycling_dict, "cycling"

    def fake_validate_file_type(filename: str) -> None:
        pass

    def fake_save_file_with_hash(content: bytes) -> tuple[str, str]:
        return ("c/ride.fit", "fhakfjkashjfa")

    monkeypatch.setattr("app.services.import_service.read_fit_file", fake_read_fit_file)
    monkeypatch.setattr("app.services.import_service.validate_file_type", fake_validate_file_type)
    monkeypatch.setattr("app.services.import_service.save_file_with_hash", fake_save_file_with_hash)
    result = await fake_import_service.import_files(test_user, [fake_uploaded_file])
    assert result == (1, 0, 0)
    assert len(fake_import_repository.uploaded_files) == 1
    assert len(fake_import_repository.workouts) == 2
    assert fake_import_repository.commit_calls == 1
    assert fake_import_repository.rollback_calls == 0


@pytest.mark.asyncio
async def test_import_files_duplicate(
    monkeypatch, test_user, fake_dup_import_repository, fake_dup_import_service, fake_uploaded_file
):
    def fake_validate_file_type(filename: str) -> None:
        pass

    monkeypatch.setattr("app.services.import_service.validate_file_type", fake_validate_file_type)
    result = await fake_dup_import_service.import_files(test_user, [fake_uploaded_file])
    assert result == (0, 1, 0)
    assert len(fake_dup_import_repository.uploaded_files) == 0
    assert len(fake_dup_import_repository.workouts) == 0
    assert fake_dup_import_repository.commit_calls == 0
    assert fake_dup_import_repository.rollback_calls == 1


@pytest.mark.asyncio
async def test_import_files_validate_error(
    monkeypatch, test_user, fake_import_repository, fake_import_service, fake_uploaded_file
):
    def fake_validate_file_type(filename: str) -> None:
        raise FileValidationError("Можно загружать только FIT-файлы!")

    monkeypatch.setattr("app.services.import_service.validate_file_type", fake_validate_file_type)
    result = await fake_import_service.import_files(test_user, [fake_uploaded_file])
    assert result == (0, 0, 1)
    assert len(fake_import_repository.uploaded_files) == 0
    assert len(fake_import_repository.workouts) == 0
    assert fake_import_repository.commit_calls == 0
    assert fake_import_repository.rollback_calls == 1


@pytest.mark.asyncio
async def test_import_files_parse_error(
    monkeypatch, fake_import_service, fake_uploaded_file, test_user, fake_import_repository
):
    del_files = []

    def read_fit_file(file_path):
        raise ParseFitError

    def fake_validate_file_type(filename: str) -> None:
        pass

    def fake_save_file_with_hash(content: bytes) -> tuple[str, str]:
        return ("c/ride.fit", "fhakfjkashjfa")

    def fake_delete_file(file_path: str) -> None:
        del_files.append(file_path)

    monkeypatch.setattr("app.services.import_service.read_fit_file", read_fit_file)
    monkeypatch.setattr("app.services.import_service.validate_file_type", fake_validate_file_type)
    monkeypatch.setattr("app.services.import_service.save_file_with_hash", fake_save_file_with_hash)
    monkeypatch.setattr("app.services.import_service.delete_file", fake_delete_file)
    result = await fake_import_service.import_files(test_user, [fake_uploaded_file])
    assert result == (0, 0, 1)
    assert len(fake_import_repository.uploaded_files) == 1
    assert len(fake_import_repository.workouts) == 0
    assert fake_import_repository.commit_calls == 0
    assert fake_import_repository.rollback_calls == 1
    assert len(del_files) == 1
    assert del_files[0] == "c/ride.fit"


@pytest.mark.asyncio
async def test_import_files_os_error(
    monkeypatch, fake_import_service, fake_uploaded_file, test_user, fake_import_repository
):

    def fake_validate_file_type(filename: str) -> None:
        pass

    def fake_save_file_with_hash(content: bytes) -> tuple[str, str]:
        raise OSError

    monkeypatch.setattr("app.services.import_service.validate_file_type", fake_validate_file_type)
    monkeypatch.setattr("app.services.import_service.save_file_with_hash", fake_save_file_with_hash)
    result = await fake_import_service.import_files(test_user, [fake_uploaded_file])
    assert result == (0, 0, 1)
    assert len(fake_import_repository.uploaded_files) == 0
    assert len(fake_import_repository.workouts) == 0
    assert fake_import_repository.commit_calls == 0
    assert fake_import_repository.rollback_calls == 1


@pytest.mark.asyncio
async def test_import_files_independent_errors(
    monkeypatch, fake_import_service, fake_uploaded_files, test_user, fake_import_repository
):

    def fake_read_fit_file(file_path: str) -> tuple[dict, str]:
        cycling_dict = {
            "timestamp": datetime(2025, 10, 8, 11, 27, 31),
            "start_time": datetime(2025, 10, 8, 10, 20, 52),
            "total_elapsed_time": 3999.0,
            "total_timer_time": 3771.0,
            "total_distance": 37146.43,
            "total_work": 810813,
            "total_moving_time": 3771.0,
            "total_calories": 819,
            "enhanced_avg_speed": 9.85,
            "avg_speed": 9.85,
            "enhanced_max_speed": 16.377,
            "max_speed": 16.377,
            "avg_power": 215,
            "max_power": 930,
            "total_ascent": 287,
            "total_descent": 293,
            "num_laps": 1,
            "normalized_power": 230,
            "training_stress_score": 93.8,
            "intensity_factor": 0.95,
            "left_right_balance": 50,
            "threshold_power": 242,
            "enhanced_avg_altitude": 185.60000000000002,
            "avg_altitude": 185.60000000000002,
            "enhanced_max_altitude": 237.20000000000005,
            "max_altitude": 237.20000000000005,
            "avg_grade": 0.37,
            "sport": "cycling",
            "sub_sport": 252,
            "avg_heart_rate": 159,
            "max_heart_rate": 180,
            "avg_cadence": 87,
            "max_cadence": 115,
            "avg_temperature": 17,
            "max_temperature": 22,
        }
        return cycling_dict, "cycling"

    def fake_save_file_with_hash(content: bytes) -> tuple[str, str]:
        return ("c/ride.fit", "fhakfjkashjfa")

    monkeypatch.setattr("app.services.import_service.read_fit_file", fake_read_fit_file)
    monkeypatch.setattr("app.services.import_service.save_file_with_hash", fake_save_file_with_hash)
    result = await fake_import_service.import_files(test_user, fake_uploaded_files)
    assert result == (2, 0, 1)
    assert len(fake_import_repository.uploaded_files) == 2
    assert len(fake_import_repository.workouts) == 4
    assert fake_import_repository.commit_calls == 2
    assert fake_import_repository.rollback_calls == 1
