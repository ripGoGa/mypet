from datetime import UTC, datetime, timedelta

import pytest

from app.models import CyclingWorkout
from app.models.models import UploadedFile, Workout
from app.models.training_models import RunningWorkout
from app.services.fit_running_parse import parse_fit_running


@pytest.fixture()
def make_workout_and_cycling(db_test_session):
    def _make(user_id, range_limit: int = 31):
        workouts = []
        for num in range(1, range_limit, 10):
            uploaded_file = UploadedFile(
                original_name="test_ride",
                sha256="test" + str(num),
                uploaded_at=datetime.now(UTC) - timedelta(days=num),
                user_id=user_id,
            )
            db_test_session.add(uploaded_file)
            db_test_session.commit()
            db_test_session.refresh(uploaded_file)
            workout = Workout(
                sport="cycling",
                started_at=datetime.now(UTC) - timedelta(days=num),
                duration=timedelta(minutes=1 + num),
                user_id=user_id,
                source_file_id=uploaded_file.id,
            )
            db_test_session.add(workout)
            db_test_session.commit()
            workouts.append(workout)
            cycling = CyclingWorkout(
                workout_id=workout.id,
                moving_time=workout.duration,
                avg_altitude=10 + num,
                avg_cadence=60 + num,
                avg_grade=2 + num // 5,
                avg_heart_rate=110 + num,
                avg_power=120 + num,
                avg_speed=20 + num // 3,
                avg_temperature=5 + num,
                max_altitude=20 + num,
                max_cadence=70 + num,
                max_heart_rate=130 + num,
                max_power=200 + num,
                max_speed=30 + num,
                max_temperature=10 + num,
                intensity_factor=2 + num // 5,
                left_right_balance=0.49,
                normalized_power=130 + num,
                threshold_power=120 + num,
                total_ascent=40 + num,
                total_descent=50 + num,
                total_distance=60 + num,
                total_calories=1000 + num,
                training_stress_score=80.0 + num,
            )
            db_test_session.add(cycling)
            db_test_session.commit()
        return workouts
    return _make


@pytest.fixture()
def make_workout_and_running(db_test_session):
    def _make(user_id, range_limit: int = 31):
        workouts = []
        for num in range(1, range_limit, 10):
            uploaded_file = UploadedFile(
                original_name="test_run",
                sha256="test_run" + str(num),
                uploaded_at=datetime.now(UTC) - timedelta(days=num),
                user_id=user_id,
            )
            db_test_session.add(uploaded_file)
            db_test_session.commit()
            db_test_session.refresh(uploaded_file)
            running_dict = {
                "sport": "running",
                "start_time": datetime.now(UTC) - timedelta(days=num),
                "timestamp": datetime(2026, 8, 31, 2, 11, 35),
                "total_elapsed_time": 2400.41 + num * 10,
                "total_timer_time": 2400.0 + num * 10,
                "total_distance": 6114.02 + num * 10,
                "total_calories": 376 + num,
                "max_heart_rate": 139 + num,
                "min_heart_rate": 64,
                "avg_heart_rate": 124 + int(num / 2),
                "avg_temperature": 32,
                "total_ascent": 0,
                "total_descent": 5,
                "total_strides": 3536 + num * 5,
                "max_running_cadence": 91,
                "avg_running_cadence": 88,
                "avg_step_length": 870.0,
                "enhanced_max_speed": 2.857,
                "max_speed": 2.857,
                "enhanced_avg_speed": 2.547,
                "avg_speed": 2.547,
                "avg_power": 189,
                "avg_stance_time": 254.0,
                "avg_stance_time_balance": 0.0,
                "avg_vertical_oscillation": 76.0,
                "avg_vertical_ratio": 8.7,
                "Effort Pace": 2.5439999103546143,
            }
            workout, clean_running_dict = parse_fit_running(
                uploaded_file_id=uploaded_file.id, user_id=user_id, session_dict=running_dict
            )
            db_test_session.add(workout)
            db_test_session.commit()
            workouts.append(workout)
            running = RunningWorkout(workout_id=workout.id, **clean_running_dict)
            db_test_session.add(running)
            db_test_session.commit()
        return workouts
    return _make
