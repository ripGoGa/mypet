from datetime import timedelta
from typing import Sequence

from app.models import CyclingWorkout
from app.models.models import Workout


class StatsCalculator:
    def __init__(self, workouts: Sequence[tuple[Workout, CyclingWorkout]]):
        self._count_workouts = len(workouts)

        # 1. Накопители общих сумм (Totals)
        self._total_distance = 0.0
        self._total_tss_num = 0.0
        self._total_ccall = 0.0
        self._total_moving_time = timedelta(0)

        # 2. Искатели максимальных пиков (Max)
        self._max_distance = 0.0
        self._max_heartrate = 0.0
        self._max_np = 0.0
        self._max_in_factor = 0.0
        self._max_ccall = 0.0

        # 3. Списки для исторических графиков (Raw Lists)
        self._raw_distance = []
        self._raw_tss = []
        self._raw_watts = []
        self._raw_speed = []
        self._raw_heartrate = []
        self._raw_cadence = []
        self._raw_in_factor = []
        self._raw_norm_power = []
        self._raw_max_hr = []
        self._raw_ccall = []
        self._raw_chart_dates = []

        # 4. Счетчики тяжести тренировок
        self.light_count = 0
        self.medium_count = 0
        self.hard_count = 0

        for workout, cycling in workouts:

            # Наполнение сумматоров (Тут 0 безопасен, так как мы просто плюсуем к общему объему)
            self._total_distance += cycling.total_distance if cycling.total_distance else 0.0
            self._total_tss_num += cycling.training_stress_score if cycling.training_stress_score else 0.0
            self._total_ccall += cycling.total_calories if cycling.total_calories else 0
            self._total_moving_time += cycling.moving_time if cycling.moving_time else timedelta(0)

            # Поиск максимумов (Обновляем ТОЛЬКО если значение прилетело из базы, игнорируя None)
            if cycling.total_distance is not None:
                self._max_distance = max(self._max_distance, cycling.total_distance)
            if cycling.max_heart_rate is not None:
                self._max_heartrate = max(self._max_heartrate, cycling.max_heart_rate)
            if cycling.normalized_power is not None:
                self._max_np = max(self._max_np, cycling.normalized_power)
            if cycling.intensity_factor is not None:
                self._max_in_factor = max(self._max_in_factor, cycling.intensity_factor)
            if cycling.total_calories is not None:
                self._max_ccall = max(self._max_ccall, cycling.total_calories)

            # Наполнение списков для графиков (Честно пишем оригинальные значения или None)
            self._raw_distance.append(cycling.total_distance)
            self._raw_tss.append(cycling.training_stress_score)
            self._raw_watts.append(cycling.avg_power)
            self._raw_speed.append(cycling.avg_speed)
            self._raw_heartrate.append(cycling.avg_heart_rate)
            self._raw_cadence.append(cycling.avg_cadence)
            self._raw_in_factor.append(cycling.intensity_factor)
            self._raw_norm_power.append(cycling.normalized_power)
            self._raw_max_hr.append(cycling.max_heart_rate)
            self._raw_ccall.append(cycling.total_calories)

            # Форматирование дат
            if workout.started_at:
                date_str = workout.started_at.strftime('%Y-%m-%d')
            else:
                date_str = "Unknown"
            self._raw_chart_dates.append(date_str)

            # Наполнение счетчиков
            if cycling.training_stress_score is None:
                pass
            elif cycling.training_stress_score <= 70:
                self.light_count += 1
            elif cycling.training_stress_score < 101:
                self.medium_count += 1
            elif cycling.training_stress_score >= 101:
                self.hard_count += 1

    # Общие объемы и Максимумы
    @property
    def count_workouts(self) -> int:
        return self._count_workouts

    @property
    def raw_total_distance(self) -> float:
        return self._total_distance

    @property
    def total_tss_num(self) -> float:
        return self._total_tss_num

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
    def max_np(self) -> float:
        return self._max_np

    @property
    def max_in_factor(self) -> float:
        return self._max_in_factor

    @property
    def max_ccall(self) -> float:
        return self._max_ccall

    @property
    def avg_watts_num(self) -> float:
        valid_data = [w for w in self._raw_watts if w is not None]
        return sum(valid_data) / len(valid_data) if valid_data else 0.0

    @property
    def avg_speed_num(self) -> float:
        valid_data = [s for s in self._raw_speed if s is not None]
        return sum(valid_data) / len(valid_data) if valid_data else 0.0

    @property
    def avg_heartrate_num(self) -> float:
        valid_data = [hr for hr in self._raw_heartrate if hr is not None]
        return sum(valid_data) / len(valid_data) if valid_data else 0.0

    @property
    def avg_cadence_num(self) -> float:
        valid_data = [c for c in self._raw_cadence if c is not None]
        return sum(valid_data) / len(valid_data) if valid_data else 0.0

    @property
    def raw_distance(self) -> list[float]:
        return self._raw_distance

    @property
    def raw_tss(self) -> list[float]:
        return self._raw_tss

    @property
    def raw_watts(self) -> list[float]:
        return self._raw_watts

    @property
    def raw_speed(self) -> list[float]:
        return self._raw_speed

    @property
    def raw_heartrate(self) -> list[float]:
        return self._raw_heartrate

    @property
    def raw_cadence(self) -> list[float]:
        return self._raw_cadence

    @property
    def raw_in_factor(self) -> list[float]:
        return self._raw_in_factor

    @property
    def raw_norm_power(self) -> list[float]:
        return self._raw_norm_power

    @property
    def raw_max_hr(self) -> list[float]:
        return self._raw_max_hr

    @property
    def raw_ccall(self) -> list[float]:
        return self._raw_ccall

    @property
    def raw_chart_dates(self) -> list[str]:
        return self._raw_chart_dates
