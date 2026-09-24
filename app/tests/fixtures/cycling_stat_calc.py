from datetime import datetime

import pytest


@pytest.fixture()
def cycling_stats_file() -> str:
    return "app/tests/data/fit/2025_10_08Ride.fit"


@pytest.fixture()
def cycling_dict():
    cycling_dict = {
        "timestamp": datetime(2025, 10, 8, 11, 27, 31),
        "start_time": datetime(2025, 10, 8, 10, 20, 52),
        "total_elapsed_time": 3999.0,
        "total_timer_time": 3771.0,
        "total_distance": 37146.43,
        "total_work": 810813,
        "total_moving_time": 3771.0,
        "total_calories": 819,
        "enhanced_avg_speed": 9.85,
        "avg_speed": 9.85,
        "enhanced_max_speed": 16.377,
        "max_speed": 16.377,
        "avg_power": 215,
        "max_power": 930,
        "total_ascent": 287,
        "total_descent": 293,
        "num_laps": 1,
        "normalized_power": 230,
        "training_stress_score": 93.8,
        "intensity_factor": 0.95,
        "left_right_balance": 50,
        "threshold_power": 242,
        "enhanced_avg_altitude": 185.60000000000002,
        "avg_altitude": 185.60000000000002,
        "enhanced_max_altitude": 237.20000000000005,
        "max_altitude": 237.20000000000005,
        "avg_grade": 0.37,
        "sport": "cycling",
        "sub_sport": 252,
        "avg_heart_rate": 159,
        "max_heart_rate": 180,
        "avg_cadence": 87,
        "max_cadence": 115,
        "avg_temperature": 17,
        "max_temperature": 22,
    }
    return cycling_dict
