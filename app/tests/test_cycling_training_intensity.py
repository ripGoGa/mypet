import pytest

from app.core.cycling_training_intensity import classify_training_intensity


@pytest.mark.parametrize(
    "tss, expected",
    [
        (None, None),
        (32, "light"),
        (70, "light"),
        (71, "medium"),
        (70.5, "medium"),
        (100, "medium"),
        (100.5, "medium"),
        (101, "hard"),
        (101.5, "hard"),
        (221, "hard"),
    ],
)
def test_classify_training_intensity(tss: float | None, expected: str | None):
    assert classify_training_intensity(tss) == expected
