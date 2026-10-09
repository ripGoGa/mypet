MIN_RUNNING_SPEED_MS = 0.6


def format_pace(speed: float | None) -> str | None:
    """Принимает скорость в м/с и выводит пейс. Нулевые и скорость ниже MIN_RUNNING_SPEED_MS возвращают None"""
    if speed is None or speed <= MIN_RUNNING_SPEED_MS:
        return None

    seconds_1km = int(1000 / speed)
    minutes, seconds = divmod(seconds_1km, 60)
    return f"{minutes}:{seconds:02d}"
