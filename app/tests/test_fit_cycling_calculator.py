import datetime

from app.services.fit_cycling_parse import parse_fit_cycling


def test_cycling_calculator_success(cycling_dict):
    workout, cycling_workout_dict = parse_fit_cycling(cycling_dict, 1, 1)
    assert workout.started_at == datetime.datetime(2025, 10, 8, 10, 20, 52)
    assert workout.duration == datetime.timedelta(seconds=3999.0)
    assert cycling_workout_dict["avg_altitude"] == 185.6
    assert cycling_workout_dict["total_distance"] == 37.15
