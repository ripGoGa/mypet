import pytest


@pytest.mark.asyncio
async def test_generate_coach_response_success(authorized_client, load_athlete_profile, load_user_profile,
                                               get_test_coach_service, db_test_session, test_user):
    user = test_user
    answer = await get_test_coach_service.generate_coach_response(user_message='fdfdfd', user=user)
    chat_history = get_test_coach_service.chat_repo.get_all_chat_history(user_id=user.id)
    assert answer == 'Ответ LLM'
    assert len(chat_history) == 2
    assert chat_history[0].role == 'user'
    assert chat_history[0].content == 'fdfdfd'
    assert chat_history[1].role == 'assistant'
    assert chat_history[1].content == 'Ответ LLM'

