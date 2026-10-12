from datetime import timedelta

import pytest
from bs4 import BeautifulSoup
from starlette.testclient import TestClient

from app.schemas.cycling_dto import CyclingStatsDTO
from app.schemas.running_dto import RunningStatsDTO
from app.services.statistics_service import StatisticsService
from app.tests.fixtures.statistics import FakeCyclingWorkoutRepository


def test_get_user_stats_success(
    test_workouts_for_cycling,
    get_fake_cycling_w_repo: FakeCyclingWorkoutRepository,
    get_fake_statistic_service: StatisticsService,
):
    result = get_fake_statistic_service.get_cycling_stats(user_id=42, period=7)
    assert isinstance(result, CyclingStatsDTO)
    assert get_fake_cycling_w_repo.history == [(42, 7)]
    assert result.count_workouts == len(test_workouts_for_cycling)


def test_get_wrong_period_returns_422(
    authorized_client: TestClient,
):
    response = authorized_client.get("/statistics?period=-1")
    assert response.status_code == 422


def test_zero_workout_stats(empty_cycling_workout_repo, empty_running_workout_repo):
    stat_service = StatisticsService(
        cycling_repo=empty_cycling_workout_repo, running_repo=empty_running_workout_repo
    )
    result_cycling = stat_service.get_cycling_stats(user_id=1)
    result_running = stat_service.get_running_stats(user_id=1)
    assert isinstance(result_cycling, CyclingStatsDTO)
    assert isinstance(result_running, RunningStatsDTO)
    assert result_cycling.count_workouts == 0
    assert result_running.count_workouts == 0
    assert result_running.avg_speed_num == 0


def test_response_statics_success(authorized_client, make_workout_and_cycling, test_user_id):
    make_workout_and_cycling(user_id=test_user_id)
    response = authorized_client.get("/statistics")

    soup = BeautifulSoup(response.text, "html.parser")

    header_dis = soup.find("div", class_="card-header", string="Макс. дистанция")
    value_div_dis = header_dis.find_next_sibling("div")

    header_hr = soup.find("div", class_="card-header", string="Макс. пульс")
    value_hr = header_hr.find_next_sibling("div")

    assert response.status_code == 200
    assert "81.0 км" in value_div_dis.get_text()
    assert "151" in value_hr.get_text()


def test_get_running_stats_success(get_fake_statistic_service: StatisticsService):
    result = get_fake_statistic_service.get_running_stats(user_id=42)
    assert isinstance(result, RunningStatsDTO)
    assert result.count_workouts == 3
    assert result.total_distance == pytest.approx(18.34, abs=0.01)
    assert result.total_moving_time == timedelta(seconds=7210)
    assert result.avg_speed_num == pytest.approx(2.543, abs=0.001)
