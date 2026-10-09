import pytest

from app.core.formatter import format_pace


@pytest.mark.parametrize(
    "speed, pace",
    [
        (5.0, "3:20"),
        (4.0, "4:10"),
        (2.5, "6:40"),
        (None, None),
        (0.5, None),
        (0.6, None),
        (3.3, "5:03"),
        (3.5, "4:45"),
    ],
)
def test_format_pace_success(speed, pace):
    assert format_pace(speed) == pace
