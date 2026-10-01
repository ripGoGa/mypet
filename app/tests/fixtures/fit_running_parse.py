from datetime import datetime

import pytest


@pytest.fixture()
def running_file() -> str:
    return "app/tests/data/fit/Morning_Run.fit"


@pytest.fixture()
def running_dict() -> dict:
    running_dict = {
        "sport": "running",
        "start_time": datetime(2026, 8, 31, 1, 31, 35),
        "timestamp": datetime(2026, 8, 31, 2, 11, 35),
        "total_elapsed_time": 2400.41,
        "total_timer_time": 2400.0,
        "total_distance": 6114.02,
        "total_calories": 376,
        "max_heart_rate": 139,
        "min_heart_rate": 64,
        "avg_heart_rate": 124,
        "avg_temperature": 32,
        "total_ascent": 0,
        "total_descent": 5,
        "total_strides": 3536,
        "max_running_cadence": 91,
        "avg_running_cadence": 88,
        "avg_step_length": 870.0,
        "enhanced_max_speed": 2.857,
        "max_speed": 2.857,
        "enhanced_avg_speed": 2.547,
        "avg_speed": 2.547,
        "avg_power": 189,
        "avg_stance_time": 254.0,
        "avg_stance_time_balance": 0.0,
        "avg_vertical_oscillation": 76.0,
        "avg_vertical_ratio": 8.7,
        "Effort Pace": 2.5439999103546143,
    }
    return running_dict