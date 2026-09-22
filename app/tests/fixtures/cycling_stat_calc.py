from pathlib import Path

import pytest


@pytest.fixture()
def cycling_stats_file() -> str:
    return "app/tests/data/fit/2025_10_08Ride.fit"