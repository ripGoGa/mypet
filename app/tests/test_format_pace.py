import pytest

from app.core.formatter import format_pace


@pytest.mark.parametrize(
    "speed, pace",
    [
        (5.0, "3:20 мин/км"),
        (4.0, "4:10 мин/км"),
        (2.5, "6:40 мин/км"),
        (None, "нет данных"),
        (0.5, "нет данных"),
        (0.6, "нет данных"),
        (3.3, "5:03 мин/км"),
        (3.5, "4:45 мин/км"),
    ],
)
def test_format_pace_success(speed, pace):
    assert format_pace(speed) == pace
