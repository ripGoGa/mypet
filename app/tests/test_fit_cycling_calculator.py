import datetime

import pytest

from app.core.exceptions import ParseFitError
from app.services.fit_cycling_parse import parse_fit_cycling


def test_cycling_calculator_success(cycling_stats_file):
    workout, cycling_workout_dict = parse_fit_cycling(cycling_stats_file, 1, 1)
    assert workout.started_at == datetime.datetime(2025, 10, 8, 10, 20, 52)
    assert workout.duration == datetime.timedelta(seconds=3999.0)
    assert cycling_workout_dict["avg_altitude"] == 185.6
    assert cycling_workout_dict["total_distance"] == 37.15

def test_cycling_calculator_miss_file_failure():
    with pytest.raises(FileNotFoundError):
        parse_fit_cycling("dadada.fut", 1, 1)


def test_cycling_calculator_broken_file_failure(tmp_path):
    broken_fit = tmp_path / "broken.fit"
    broken_fit.write_bytes(b"dadadads")
    with pytest.raises(ParseFitError):
        parse_fit_cycling(str(broken_fit), 1, 1)