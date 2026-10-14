import pytest

from app.core.formatter import format_stats


@pytest.mark.parametrize(
    "num, metric, result",
    [
        (25.121, "км.", "25.12 км."),
        (None, "", "нет данных"),
        (-1, "градусов", "-1 градусов"),
        (0, "", "нет данных"),
        (0.0, "", "нет данных"),
        (0.86, "", "0.86"),
        (43.434322131, "метра", "43.43 метра"),
    ],
)
def test_format_stats_success(num, metric, result):
    assert format_stats(num, metric) == result
