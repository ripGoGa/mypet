import pytest, re

from app.core.exceptions import AIProviderNotAvailable
from app.models.models import ChatMessage, Users
from app.services.statistics_service import StatisticsService
from app.tests.fixtures.coach import BrokenFakeLLMProvider


@pytest.mark.usefixtures("load_athlete_profile", "load_user_profile")
@pytest.mark.asyncio
async def test_generate_coach_response_success(
    make_coach_service,
    test_user,
):
    test_coach_service = make_coach_service()
    answer = await test_coach_service.generate_coach_response(user_message="fdfdfd", user=test_user)
    chat_history = test_coach_service.chat_repo.get_all_chat_history(user_id=test_user.id)
    assert answer == "Ответ LLM"
    assert len(chat_history) == 2
    assert chat_history[0].role == "user"
    assert chat_history[0].content == "fdfdfd"
    assert chat_history[1].role == "assistant"
    assert chat_history[1].content == "Ответ LLM"


@pytest.mark.usefixtures("load_athlete_profile", "load_user_profile")
@pytest.mark.asyncio
async def test_generate_coach_error(make_coach_service, test_user):
    broken_coach_service = make_coach_service(llm_provider=BrokenFakeLLMProvider())
    with pytest.raises(AIProviderNotAvailable):
        await broken_coach_service.generate_coach_response(user_message="user message", user=test_user)

    chat_history = broken_coach_service.chat_repo.get_all_chat_history(user_id=test_user.id)
    assert len(chat_history) == 0


@pytest.mark.asyncio
async def test_coach_service_get_chat_history(make_coach_service, test_user):
    test_coach_service = make_coach_service()
    test_coach_service.chat_repo.save_message(ChatMessage(user_id=test_user.id, role="user", content="fdfdfd"))
    test_coach_service.chat_repo.save_message(ChatMessage(user_id=test_user.id, role="assistant", content="hi"))
    test_coach_service.chat_repo.commit()
    chat_history = test_coach_service.get_chat_history(user_id=test_user.id)
    assert len(chat_history) == 2
    assert chat_history[0].role == "user"
    assert chat_history[0].content == "fdfdfd"
    assert chat_history[1].role == "assistant"
    assert chat_history[1].content == "hi"


def test_build_workouts_only_cycling(make_coach_service, get_fake_cycling_w_repo, empty_running_workout_repo):
    coach_service = make_coach_service(
        stat_service=StatisticsService(cycling_repo=get_fake_cycling_w_repo, running_repo=empty_running_workout_repo)
    )

    result = coach_service._build_workouts(user=Users(id=42))

    assert "Статистика вело тренировок" in result
    assert "Статистика беговых" not in result


def test_build_workouts_only_running(make_coach_service, get_fake_running_w_repo, empty_cycling_workout_repo):
    coach_service = make_coach_service(
        stat_service=StatisticsService(running_repo=get_fake_running_w_repo, cycling_repo=empty_cycling_workout_repo)
    )

    result = coach_service._build_workouts(user=Users(id=42))

    assert "Статистика вело тренировок" not in result
    assert "Статистика беговых" in result


def test_build_workouts_cycling_and_running(make_coach_service):
    coach_service = make_coach_service()

    result = coach_service._build_workouts(user=Users(id=42))

    assert "Статистика вело тренировок" in result
    assert "Статистика беговых" in result
    assert "\n\n" in result


def test_build_workouts_empty(make_coach_service, empty_cycling_workout_repo, empty_running_workout_repo):
    coach_service = make_coach_service(
        stat_service=StatisticsService(cycling_repo=empty_cycling_workout_repo, running_repo=empty_running_workout_repo)
    )

    result = coach_service._build_workouts(user=Users(id=42))

    assert "Тренировки не найдены." == result


@pytest.mark.usefixtures("load_athlete_profile", "load_user_profile")
@pytest.mark.asyncio
async def test_generate_coach_response_sends_workout_summary_to_llm(make_coach_service, test_user):
    coach_service = make_coach_service()

    await coach_service.generate_coach_response(user=test_user, user_message="user message")

    user_message = coach_service.llm_provider.history_messages[-1][-1]
    assert user_message["role"] == "user"
    assert coach_service.llm_provider.history_messages[-1][0]["role"] == "system"
    assert "Статистика вело тренировок" in user_message["content"]
    assert "Статистика беговых тренировок" in user_message["content"]

@pytest.mark.usefixtures("load_athlete_profile", "load_user_profile")
@pytest.mark.asyncio
async def test_generate_coach_response_prompt_has_no_unfilled_placeholders(make_coach_service, test_user):
    """Проверяем только системное сообщение"""
    coach_service = make_coach_service()

    await coach_service.generate_coach_response(user=test_user, user_message="user message")

    system_message = coach_service.llm_provider.history_messages[-1][0]
    text = system_message["content"]
    assert "{" not in text
    assert "}" not in text