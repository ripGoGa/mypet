import pytest

from app.core.exceptions import AIProviderNotAvailable
from app.models.models import ChatMessage
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
    with pytest.raises(AIProviderNotAvailable):
        broken_coach_service = make_coach_service(llm_provider=BrokenFakeLLMProvider())
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
