import pytest
from pydantic import ValidationError

from app.core.dependencies import get_workout_service
from app.core.exceptions import CorruptedDataError, MissingWorkoutError
from app.models import CyclingWorkout, RunningWorkout
from app.models.models import Workout
from app.schemas.cycling_workout_detail_dto import CyclingWorkoutDetailDTO
from app.schemas.running_workout_detail_dto import RunningWorkoutDetailDTO
from app.services.workout_service import WorkoutService
from app.tests.fixtures.model_factories import make_cycling_workout, make_running_workout, make_workout


class StubWorkoutRepository:
    def __init__(self, workout: Workout | None = None):
        self.workout = workout

    def get_one_workout(self, user_id, workout_id) -> Workout | None:
        return self.workout


class StubSportWorkoutRepository:
    def __init__(self, sport_workout: CyclingWorkout | RunningWorkout | None = None):
        self.sport_workout = sport_workout
        self.calls = []

    def get_by_workout_id(self, workout_id, user_id) -> CyclingWorkout | RunningWorkout | None:
        self.calls.append((workout_id, user_id))
        return self.sport_workout


def make_workout_service(
    *,
    work_repo: StubWorkoutRepository | None = None,
    cycling_repo: StubSportWorkoutRepository | None = None,
    running_repo: StubSportWorkoutRepository | None = None,
) -> WorkoutService:
    if work_repo is None:
        work_repo = StubWorkoutRepository()
    if cycling_repo is None:
        cycling_repo = StubSportWorkoutRepository()
    if running_repo is None:
        running_repo = StubSportWorkoutRepository()
    return WorkoutService(work_repo=work_repo, cycling_repo=cycling_repo, running_repo=running_repo)


def test_workout_service_get_user_workout_running_success():
    workout = make_workout(sport="running")
    running_workout = make_running_workout(total_calories=100)
    running_repo = StubSportWorkoutRepository(sport_workout=running_workout)
    cycling_repo = StubSportWorkoutRepository()
    workout_service = make_workout_service(
        work_repo=StubWorkoutRepository(workout), running_repo=running_repo, cycling_repo=cycling_repo
    )

    result = workout_service.get_user_workout(workout_id=workout.id, user_id=workout.user_id)

    assert running_repo.calls == [(workout.id, workout.user_id)]
    assert isinstance(result, RunningWorkoutDetailDTO)
    assert result.calories == 100
    assert cycling_repo.calls == []


def test_workout_service_get_user_workout_cycling_success():
    workout = make_workout(sport="cycling")
    cycling_workout = make_cycling_workout(total_calories=100)
    running_repo = StubSportWorkoutRepository()
    cycling_repo = StubSportWorkoutRepository(sport_workout=cycling_workout)
    workout_service = make_workout_service(
        work_repo=StubWorkoutRepository(workout), running_repo=running_repo, cycling_repo=cycling_repo
    )

    result = workout_service.get_user_workout(workout_id=workout.id, user_id=workout.user_id)

    assert cycling_repo.calls == [(workout.id, workout.user_id)]
    assert isinstance(result, CyclingWorkoutDetailDTO)
    assert result.calories == 100
    assert running_repo.calls == []


def test_workout_service_workout_is_missing():
    cycling_workout = make_cycling_workout()
    running_workout = make_running_workout()
    running_repo = StubSportWorkoutRepository(running_workout)
    cycling_repo = StubSportWorkoutRepository(cycling_workout)
    workout_service = make_workout_service(
        work_repo=StubWorkoutRepository(), running_repo=running_repo, cycling_repo=cycling_repo
    )

    with pytest.raises(MissingWorkoutError):
        workout_service.get_user_workout(workout_id=10, user_id=1)

    assert cycling_repo.calls == []
    assert running_repo.calls == []


def test_workout_service_workout_is_unknown_sport():
    workout = make_workout(sport="swimming")
    cycling_workout = make_cycling_workout()
    running_workout = make_running_workout()
    running_repo = StubSportWorkoutRepository(running_workout)
    cycling_repo = StubSportWorkoutRepository(cycling_workout)
    workout_service = make_workout_service(
        work_repo=StubWorkoutRepository(workout), running_repo=running_repo, cycling_repo=cycling_repo
    )

    with pytest.raises(CorruptedDataError):
        workout_service.get_user_workout(workout_id=11, user_id=1)
    assert cycling_repo.calls == []
    assert running_repo.calls == []


def test_workout_service_workout_raises_corrupted_data_when_sport_record_missing():
    workout = make_workout(sport="running")
    cycling_workout = make_cycling_workout()
    running_repo = StubSportWorkoutRepository()
    cycling_repo = StubSportWorkoutRepository(cycling_workout)
    workout_service = make_workout_service(
        work_repo=StubWorkoutRepository(workout), running_repo=running_repo, cycling_repo=cycling_repo
    )

    with pytest.raises(CorruptedDataError):
        workout_service.get_user_workout(workout_id=11, user_id=1)
    assert cycling_repo.calls == []
    assert running_repo.calls == [(11, 1)]


def test_workout_service_raises_corrupted_data_when_dto_error():
    workout = make_workout(sport="running")
    cycling_workout = make_cycling_workout()
    running_workout = make_running_workout(total_timer_time=None)
    running_repo = StubSportWorkoutRepository(running_workout)
    cycling_repo = StubSportWorkoutRepository(cycling_workout)
    workout_service = make_workout_service(
        work_repo=StubWorkoutRepository(workout), running_repo=running_repo, cycling_repo=cycling_repo
    )

    with pytest.raises(CorruptedDataError) as exc_info:
        workout_service.get_user_workout(workout_id=11, user_id=1)
    assert isinstance(exc_info.value.__cause__, ValidationError)
    assert cycling_repo.calls == []
    assert running_repo.calls == [(11, 1)]


def test_get_user_workout_returns_running_dto_from_db(db_test_session, test_user_id, make_workout_and_running):
    running_workouts = make_workout_and_running(user_id=test_user_id, range_limit=10)
    service = get_workout_service(session=db_test_session)

    result_running = service.get_user_workout(workout_id=running_workouts[0].id, user_id=test_user_id)

    assert isinstance(result_running, RunningWorkoutDetailDTO)
    assert result_running.workout_id == running_workouts[0].id


def test_get_user_workout_returns_cycling_dto_from_db(db_test_session, test_user_id, make_workout_and_cycling):
    cycling_workouts = make_workout_and_cycling(user_id=test_user_id, range_limit=10)
    service = get_workout_service(session=db_test_session)

    result_cycling = service.get_user_workout(workout_id=cycling_workouts[0].id, user_id=test_user_id)

    assert isinstance(result_cycling, CyclingWorkoutDetailDTO)
    assert result_cycling.workout_id == cycling_workouts[0].id


def test_get_user_workout_raises_missing_for_other_users_workout(
    db_test_session, test_user_id, second_user_id, make_workout_and_cycling
):
    second_user_workouts = make_workout_and_cycling(user_id=second_user_id, range_limit=10)
    make_workout_and_cycling(user_id=test_user_id, range_limit=10)

    service = get_workout_service(session=db_test_session)

    assert second_user_workouts[0].id is not None

    with pytest.raises(MissingWorkoutError):
        service.get_user_workout(user_id=test_user_id, workout_id=second_user_workouts[0].id)
