from datetime import timedelta

MIN_RUNNING_SPEED_MS = 0.6


def format_pace(speed: float | None) -> str:
    """Принимает скорость в м/с и выводит пейс. Нулевые и скорость ниже MIN_RUNNING_SPEED_MS возвращают "нет данных"""
    if speed is None or speed <= MIN_RUNNING_SPEED_MS:
        return "нет данных"

    seconds_1km = int(1000 / speed)
    minutes, seconds = divmod(seconds_1km, 60)
    return f"{minutes}:{seconds:02d} мин/км"


def format_stats(num: int | float | None, metric: str = "") -> str:
    """Принимает данные и проверяет их корректность, возвращая результирующую строку"""
    if num is None or num == 0:
        return "нет данных"
    return f"{round(num, 2)} {metric}".strip(" ")


def format_time(time: timedelta | None) -> str:
    """Переводит большие временные отрезки в часы и выводит строку вида ч:мм:сс"""
    if time is None or time.total_seconds() == 0:
        return "нет данных"
    hours, seconds = divmod(time.total_seconds(), 3600)
    minutes, seconds = divmod(seconds, 60)
    return f"{int(hours)}:{int(minutes):02d}:{int(seconds):02d}"
