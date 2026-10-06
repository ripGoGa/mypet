from datetime import timedelta
from typing import Sequence

from app.models.models import Workout
from app.models.training_models import RunningWorkout


class RunningStatsCalculator:
    def __init__(self, workouts: Sequence[tuple[Workout, RunningWorkout]]):
        self._count_workouts = len(workouts)

        # 1. Накопители общих сумм (Totals)
        self._total_distance = 0.0
        self._total_ccall = 0.0
        self._total_moving_time = timedelta(0)

        # 2. Искатели максимальных пиков (Max)
        self._max_distance = 0.0
        self._max_heartrate = 0.0
        self._max_ccall = 0.0

        # 3. Списки для исторических графиков (Raw Lists)
        self._raw_distance = []
        self._raw_speed = []
        self._raw_heartrate = []
        self._raw_cadence = []
        self._raw_max_hr = []
        self._raw_ccall = []
        self._raw_chart_dates = []

        for workout, running in workouts:
            # Наполнение сумматоров (Тут 0 безопасен, так как мы просто плюсуем к общему объему)
            self._total_distance += running.total_distance if running.total_distance else 0.0
            self._total_ccall += running.total_calories if running.total_calories else 0
            self._total_moving_time += running.moving_time if running.moving_time else timedelta(0)

            # Поиск максимумов (Обновляем ТОЛЬКО если значение прилетело из базы, игнорируя None)
            if running.total_distance is not None:
                self._max_distance = max(self._max_distance, running.total_distance)
            if running.max_heart_rate is not None:
                self._max_heartrate = max(self._max_heartrate, running.max_heart_rate)
            if running.total_calories is not None:
                self._max_ccall = max(self._max_ccall, running.total_calories)

            # Наполнение списков для графиков (Честно пишем оригинальные значения или None)
            self._raw_distance.append(running.total_distance)
            self._raw_speed.append(running.avg_speed)
            self._raw_heartrate.append(running.avg_heart_rate)
            self._raw_cadence.append(running.avg_running_cadence * 2
                                                if running.avg_running_cadence  is not None
                                                else None)
            self._raw_max_hr.append(running.max_heart_rate)
            self._raw_ccall.append(running.total_calories)

            # Форматирование дат
            if workout.started_at:
                date_str = workout.started_at.strftime("%Y-%m-%d")
            else:
                date_str = "Unknown"
            self._raw_chart_dates.append(date_str)

    # Общие объемы и Максимумы
    @property
    def count_workouts(self) -> int:
        return self._count_workouts

    @property
    def total_distance(self) -> float:
        return self._total_distance

    @property
    def total_moving_time(self) -> timedelta:
        return self._total_moving_time

    @property
    def total_ccall(self) -> float:
        return self._total_ccall

    @property
    def max_distance(self) -> float:
        return self._max_distance

    @property
    def max_heartrate(self) -> float:
        return self._max_heartrate

    @property
    def max_ccall(self) -> float:
        return self._max_ccall

    @property
    def avg_speed_num(self) -> float:
        return (
            self._total_distance * 1000 / self._total_moving_time.total_seconds()
            if self._total_moving_time
            else 0.0
        )

    @property
    def avg_heartrate_num(self) -> float:
        valid_data = [hr for hr in self._raw_heartrate if hr is not None]
        return sum(valid_data) / len(valid_data) if valid_data else 0.0

    @property
    def avg_cadence_num(self) -> float:
        valid_data = [c for c in self._raw_cadence if c is not None]
        return sum(valid_data) / len(valid_data) if valid_data else 0.0

    @property
    def raw_distance(self) -> list[float | None]:
        return self._raw_distance

    @property
    def raw_speed(self) -> list[float | None]:
        return self._raw_speed

    @property
    def raw_heartrate(self) -> list[float | None]:
        return self._raw_heartrate

    @property
    def raw_cadence(self) -> list[float | None]:
        return self._raw_cadence

    @property
    def raw_max_hr(self) -> list[float | None]:
        return self._raw_max_hr

    @property
    def raw_ccall(self) -> list[float | None]:
        return self._raw_ccall

    @property
    def raw_chart_dates(self) -> list[str]:
        return self._raw_chart_dates
