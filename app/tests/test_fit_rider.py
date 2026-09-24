import pytest

from app.core.exceptions import ParseFitError
from app.services.read_fit_file import read_fit_file


def test_read_fit_file_success(cycling_stats_file):
    stats_dict, sport = read_fit_file(cycling_stats_file)
    assert isinstance(stats_dict, dict)
    assert sport == 'cycling'
    assert stats_dict["enhanced_max_speed"] == 16.377


def test_read_fit_file_failure():
    with pytest.raises(FileNotFoundError):
        read_fit_file("dadada.fut")


def test_пread_fit_file_broken_file_failure(tmp_path):
    broken_fit = tmp_path / "broken.fit"
    broken_fit.write_bytes(b"dadadads")
    with pytest.raises(ParseFitError):
        read_fit_file(str(broken_fit))
