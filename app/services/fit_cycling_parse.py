from datetime import timedelta
from pathlib import Path
from typing import Tuple

import fitparse
from app.core.exceptions import MultiSessionError, ParseFitError, ZeroSessionError
from app.models.models import Workout


def parse_fit_cycling(
    file_path: str, user_id: int, uploaded_file_id: int
) -> Tuple[Workout, dict]:
    try:
        fit_file = fitparse.FitFile(file_path)
        session_data = list(fit_file.get_messages("session"))
        if len(session_data) > 1:
            raise MultiSessionError
        if len(session_data) == 0:
            raise ZeroSessionError
        session = session_data[0].get_values()
        workout = Workout(sport=session.get("sport"),
                          started_at=session.get("start_time"),
                          duration=timedelta(seconds=session.get("total_elapsed_time")),
                          user_id=user_id,
                          source_file_id=uploaded_file_id)

        cycling_w_dict = dict()
        cycling_w_dict["moving_time"] = timedelta(seconds=session.get("total_timer_time"))
        cycling_w_dict["avg_altitude"] = round(session.get("enhanced_avg_altitude"), 1)
        cycling_w_dict["avg_cadence"] = session.get("avg_cadence")
        cycling_w_dict["avg_grade"] = session.get("avg_grade")
        cycling_w_dict["avg_heart_rate"] = session.get("avg_heart_rate")
        cycling_w_dict["avg_power"] = session.get("avg_power")
        cycling_w_dict["avg_speed"] = session.get("enhanced_avg_speed") * 3.6
        cycling_w_dict["avg_temperature"] = session.get("avg_temperature")

        cycling_w_dict["max_altitude"] = session.get("enhanced_max_altitude")
        cycling_w_dict["max_cadence"] = session.get("max_cadence")
        cycling_w_dict["max_heart_rate"] = session.get("max_heart_rate")
        cycling_w_dict["max_power"] = session.get("max_power")
        cycling_w_dict["max_speed"] = session.get("enhanced_max_speed") * 3.6
        cycling_w_dict["max_temperature"] = session.get("max_temperature")

        cycling_w_dict["intensity_factor"] = session.get("intensity_factor")
        cycling_w_dict["left_right_balance"] = session.get("left_right_balance")
        cycling_w_dict["normalized_power"] = session.get("normalized_power")
        cycling_w_dict["threshold_power"] = session.get("threshold_power")

        cycling_w_dict["total_ascent"] = session.get("total_ascent")
        cycling_w_dict["total_descent"] = session.get("total_descent")
        cycling_w_dict["total_distance"] = round(session.get("total_distance") / 1000, 2)
        cycling_w_dict["total_calories"] = session.get("total_calories")
        cycling_w_dict["training_stress_score"] = session.get("training_stress_score")

    except fitparse.FitParseError as err:
        raise ParseFitError from err

    return workout, cycling_w_dict





