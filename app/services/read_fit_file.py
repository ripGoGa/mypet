from typing import Tuple

import fitparse
from app.core.exceptions import MultiSessionError, NoSportError, ParseFitError, ZeroSessionError


def read_fit_file(file_path: str) -> Tuple[dict, str]:
    try:
        fit_file = fitparse.FitFile(file_path)
        session_data = list(fit_file.get_messages("session"))
        if len(session_data) > 1:
            raise MultiSessionError
        if len(session_data) == 0:
            raise ZeroSessionError
        session = session_data[0].get_values()
        sport = session.get("sport")
        if sport is None:
            raise NoSportError
        return session, sport

    except fitparse.FitParseError as err:
        raise ParseFitError from err

