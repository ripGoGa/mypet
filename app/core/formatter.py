MIN_RUNNING_SPEED = 0.6

def format_pace(speed: float | int | None) -> str | None:
    """Принимает скорость в м/с и выводит пейс. Нулевые и некорректно медленный темп возвращает None"""
    if speed is None or speed <= MIN_RUNNING_SPEED:
        return None

    seconds_1km = int(1000 / speed)
    minutes, seconds = divmod(seconds_1km, 60)
    return f'{minutes}:{seconds:02d}'