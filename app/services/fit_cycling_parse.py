from datetime import timedelta
from typing import Tuple

from app.models.models import Workout


def parse_fit_cycling(session_dict: dict, user_id: int, uploaded_file_id: int) -> Tuple[Workout, dict]:
    workout = Workout(
        sport=session_dict.get("sport"),
        started_at=session_dict.get("start_time"),
        duration=timedelta(seconds=session_dict.get("total_elapsed_time")),
        user_id=user_id,
        source_file_id=uploaded_file_id,
    )

    cycling_w_dict = dict()
    cycling_w_dict["moving_time"] = timedelta(seconds=session_dict.get("total_timer_time"))
    cycling_w_dict["avg_altitude"] = round(session_dict.get("enhanced_avg_altitude"), 1)
    cycling_w_dict["avg_cadence"] = session_dict.get("avg_cadence")
    cycling_w_dict["avg_grade"] = session_dict.get("avg_grade")
    cycling_w_dict["avg_heart_rate"] = session_dict.get("avg_heart_rate")
    cycling_w_dict["avg_power"] = session_dict.get("avg_power")
    cycling_w_dict["avg_speed"] = session_dict.get("enhanced_avg_speed") * 3.6
    cycling_w_dict["avg_temperature"] = session_dict.get("avg_temperature")

    cycling_w_dict["max_altitude"] = session_dict.get("enhanced_max_altitude")
    cycling_w_dict["max_cadence"] = session_dict.get("max_cadence")
    cycling_w_dict["max_heart_rate"] = session_dict.get("max_heart_rate")
    cycling_w_dict["max_power"] = session_dict.get("max_power")
    cycling_w_dict["max_speed"] = session_dict.get("enhanced_max_speed") * 3.6
    cycling_w_dict["max_temperature"] = session_dict.get("max_temperature")

    cycling_w_dict["intensity_factor"] = session_dict.get("intensity_factor")
    cycling_w_dict["left_right_balance"] = session_dict.get("left_right_balance")
    cycling_w_dict["normalized_power"] = session_dict.get("normalized_power")
    cycling_w_dict["threshold_power"] = session_dict.get("threshold_power")

    cycling_w_dict["total_ascent"] = session_dict.get("total_ascent")
    cycling_w_dict["total_descent"] = session_dict.get("total_descent")
    cycling_w_dict["total_distance"] = round(session_dict.get("total_distance") / 1000, 2)
    cycling_w_dict["total_calories"] = session_dict.get("total_calories")
    cycling_w_dict["training_stress_score"] = session_dict.get("training_stress_score")
    return workout, cycling_w_dict
