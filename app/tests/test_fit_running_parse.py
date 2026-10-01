import datetime

from app.models.training_models import RunningWorkout
from app.services.fit_running_parse import parse_fit_running


def test_parse_fit_running_success(running_dict) -> None:
    workout, clean_running_dict = parse_fit_running(running_dict, user_id=1, uploaded_file_id=2)
    running_workout = RunningWorkout(workout_id = workout.id, **clean_running_dict)
    assert workout.started_at == datetime.datetime(2026, 8, 31, 1, 31, 35)
    assert workout.duration == datetime.timedelta(seconds=2400.41)
    assert workout.sport == "running"
    assert workout.user_id == 1
    assert clean_running_dict["total_distance"] == 6.11
    assert clean_running_dict["effort_pace"] == 2.5439999103546143
    assert clean_running_dict["avg_stance_time"] == 254.0
    assert clean_running_dict["total_elapsed_time"] == 2400.41
    assert clean_running_dict["moving_time"] == datetime.timedelta(seconds=2400.0)
    assert running_workout.avg_step_length == 870.0
    assert running_workout.avg_stance_time_balance == 0.0