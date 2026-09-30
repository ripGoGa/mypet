from datetime import timedelta
from typing import Tuple

from app.models.models import Workout


def parse_fit_running(session_dict: dict, user_id: int, uploaded_file_id: int) -> Tuple[Workout, dict]:
    workout = Workout(
        sport=session_dict.get("sport"),
        started_at=session_dict.get("start_time"),
        duration=timedelta(seconds=session_dict.get("total_elapsed_time")),
        user_id=user_id,
        source_file_id=uploaded_file_id,
    )


    running_w_dict = dict()
    running_w_dict["moving_time"] = timedelta(seconds=session_dict.get("total_timer_time"))
    running_w_dict["avg_heart_rate"] = session_dict.get("avg_heart_rate")
    running_w_dict["avg_power"] = session_dict.get("avg_power")
    running_w_dict["avg_running_cadence"] = session_dict.get("avg_running_cadence")
    running_w_dict["avg_speed"] = session_dict.get("avg_speed")
    running_w_dict["avg_stance_time"] = session_dict.get("avg_stance_time")
    running_w_dict["avg_stance_time_balance"] = session_dict.get("avg_stance_time_balance")

    running_w_dict["avg_step_length"] = session_dict.get("avg_step_length")
    running_w_dict["avg_temperature"] = session_dict.get("avg_temperature")
    running_w_dict["avg_vertical_oscillation"] = session_dict.get("avg_vertical_oscillation")
    running_w_dict["avg_vertical_ratio"] = session_dict.get("avg_vertical_ratio")
    running_w_dict["effort_pace"] = session_dict.get("Effort Pace")

    running_w_dict["max_heart_rate"] = session_dict.get("max_heart_rate")
    running_w_dict["max_running_cadence"] = session_dict.get("max_running_cadence")
    running_w_dict["max_speed"] = session_dict.get("max_speed")

    running_w_dict["total_ascent"] = session_dict.get("total_ascent")
    running_w_dict["total_descent"] = session_dict.get("total_descent")
    running_w_dict["total_distance"] = round(session_dict.get("total_distance") / 1000, 2)
    running_w_dict["total_calories"] = session_dict.get("total_calories")
    running_w_dict["total_elapsed_time"] = session_dict.get("total_elapsed_time")
    running_w_dict["total_strides"] = session_dict.get("total_strides")
    running_w_dict["total_timer_time"] = session_dict.get("total_timer_time")
    return workout, running_w_dict
