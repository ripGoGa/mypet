import pytest
from sqlmodel import select

from app.models.models import Users


@pytest.mark.asyncio
async def test_generate_coach_response_success(authorized_client, load_athlete_profile, load_user_profile,
                                               get_test_coach_service, db_test_session, test_user):
    user = test_user
    answer = await get_test_coach_service.generate_coach_response(user_message='fdfdfd', user=user)
    assert answer == 'Ответ LLM'
