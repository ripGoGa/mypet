import pytest

from app.core.exceptions import ParseFitError, NoSportError
from app.services.read_fit_file import read_fit_file
from unittest.mock import patch, MagicMock


def test_read_fit_file_success(cycling_stats_file):
    stats_dict, sport = read_fit_file(cycling_stats_file)
    assert isinstance(stats_dict, dict)
    assert sport == "cycling"
    assert stats_dict["enhanced_max_speed"] == 16.377


def test_read_fit_file_failure():
    with pytest.raises(FileNotFoundError):
        read_fit_file("dadada.fut")


def test_read_fit_file_broken_file_failure(tmp_path):
    broken_fit = tmp_path / "broken.fit"
    broken_fit.write_bytes(b"dadadads")
    with pytest.raises(ParseFitError):
        read_fit_file(str(broken_fit))


def test_read_fit_file_no_sport(cycling_stats_file):
    fake_session_dict = MagicMock()
    fake_session_dict.get_values.return_value = {"enhanced_max_speed": 16.377}
    with patch("fitparse.FitFile.get_messages", return_value=[fake_session_dict]):
        with pytest.raises(NoSportError):
            read_fit_file(cycling_stats_file)
