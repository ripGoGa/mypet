from datetime import timedelta

import pytest

from app.core.formatter import format_time


@pytest.mark.parametrize(
    "time, result",
    [
        (None, "нет данных"),
        (timedelta(hours=3, minutes=61), "4:01:00"),
        (timedelta(seconds=59), "0:00:59"),
        (timedelta(hours=1), "1:00:00"),
        (timedelta(hours=26, seconds=9), "26:00:09"),
        (timedelta(), "нет данных"),
    ],
)
def test_format_time(time, result):
    assert format_time(time) == result
