import pytest

from app.core.exceptions import AIProviderNotAvailable
from app.repository.chat_repo import ChatRepository
from app.repository.workout_repo import WorkoutRepository
from app.services.coach_service import CoachService


class FakeLLMProvider:
    def __init__(self):
        self.history_messages = []

    async def send_message(self, messages: list[dict[str, str]]) -> str:
        self.history_messages.append(messages)
        return 'Ответ LLM'


class BrokenFakeLLMProvider:
    def __init__(self):
        self.history_messages = []

    async def send_message(self, messages: list[dict[str, str]]) -> str:
        self.history_messages.append(messages)
        raise AIProviderNotAvailable


@pytest.fixture()
def fake_llm_provider():
    return FakeLLMProvider()


@pytest.fixture()
def get_test_coach_service(db_test_session) -> CoachService:
    workout_repo = WorkoutRepository(session=db_test_session)
    chat_repo = ChatRepository(session=db_test_session)
    llm_provider = FakeLLMProvider()
    new_coach_service = CoachService(workout_repo=workout_repo, chat_repo=chat_repo, llm_provider=llm_provider)
    return new_coach_service


@pytest.fixture()
def get_test_broken_coach_service(db_test_session) -> CoachService:
    workout_repo = WorkoutRepository(session=db_test_session)
    chat_repo = ChatRepository(session=db_test_session)
    llm_provider = BrokenFakeLLMProvider()
    new_coach_service = CoachService(workout_repo=workout_repo, chat_repo=chat_repo, llm_provider=llm_provider)
    return new_coach_service