from bs4 import BeautifulSoup

from app.schemas.workoutDTO import WorkoutsDTO
from app.services.statistics_service import StatisticsService
from app.tests.fixtures.statistics import FakeCyclingWorkoutRepository



def test_get_user_stats_success(test_workouts, get_fake_cycling_w_repo: FakeCyclingWorkoutRepository,
                                get_fake_statistic_service: StatisticsService):
    result = get_fake_statistic_service.get_user_stats(user_id=42, period=7)
    assert isinstance(result, WorkoutsDTO)
    assert get_fake_cycling_w_repo.history == [(42, 7)]
    assert result.count_workouts == len(test_workouts)


def test_zero_workout_stats(empty_cycling_workout_repo):
    result = StatisticsService(cycling_repo=empty_cycling_workout_repo,
                               workout_repo=None).get_user_stats(user_id=1)
    assert isinstance(result, WorkoutsDTO)
    assert result.count_workouts == 0


def test_response_statics_success(authorized_client, load_workout_and_cycling):
    response = authorized_client.get("/statistics")

    soup = BeautifulSoup(response.text, "html.parser")

    header_dis = soup.find("div", class_="card-header", string="Макс. дистанция")
    value_div_dis = header_dis.find_next_sibling("div")

    header_hr = soup.find("div", class_="card-header", string='Макс. пульс')
    value_hr = header_hr.find_next_sibling("div")

    assert response.status_code == 200
    assert "81.0 км" in value_div_dis.get_text()
    assert "151" in value_hr.get_text()

