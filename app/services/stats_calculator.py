from datetime import timedelta
from typing import Sequence

from app.models.models import Workout


class StatsCalculator:
    def __init__(self, workouts: Sequence[Workout]):
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

        for workout in workouts:

            # Наполнение сумматоров (Тут 0 безопасен, так как мы просто плюсуем к общему объему)
            self._total_distance += workout.distance_km if workout.distance_km else 0.0
            self._total_tss_num += workout.training_stress_score if workout.training_stress_score else 0.0
            self._total_ccall += workout.calories_burned if workout.calories_burned else 0
            self._total_moving_time += workout.moving_time if workout.moving_time else timedelta(0)

            # Поиск максимумов (Обновляем ТОЛЬКО если значение прилетело из базы, игнорируя None)
            if workout.distance_km is not None:
                self._max_distance = max(self._max_distance, workout.distance_km)
            if workout.max_heartrate is not None:
                self._max_heartrate = max(self._max_heartrate, workout.max_heartrate)
            if workout.normalized_power is not None:
                self._max_np = max(self._max_np, workout.normalized_power)
            if workout.intensity_factor is not None:
                self._max_in_factor = max(self._max_in_factor, workout.intensity_factor)
            if workout.calories_burned is not None:
                self._max_ccall = max(self._max_ccall, workout.calories_burned)

            # Наполнение списков для графиков (Честно пишем оригинальные значения или None)
            self._raw_distance.append(workout.distance_km)
            self._raw_tss.append(workout.training_stress_score)
            self._raw_watts.append(workout.avg_watts)
            self._raw_speed.append(workout.avg_speed)
            self._raw_heartrate.append(workout.avg_heartrate)
            self._raw_cadence.append(workout.avg_cadence)
            self._raw_in_factor.append(workout.intensity_factor)
            self._raw_norm_power.append(workout.normalized_power)
            self._raw_max_hr.append(workout.max_heartrate)
            self._raw_ccall.append(workout.calories_burned)

            # Форматирование дат
            if workout.source_file and workout.source_file.uploaded_at:
                date_str = workout.source_file.uploaded_at.strftime('%Y-%m-%d')
            else:
                date_str = "Unknown"
            self._raw_chart_dates.append(date_str)

            # Наполнение счетчиков
            if workout.training_stress_score is None:
                self.light_count += 1
            elif workout.training_stress_score <= 70:
                self.light_count += 1
            elif workout.training_stress_score < 101:
                self.medium_count += 1
            elif workout.training_stress_score >= 101:
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
