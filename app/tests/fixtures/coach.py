import pytest

from app.core.exceptions import AIProviderNotAvailable
from app.infrastructure.llm.llm_protocol import LLMProvider
from app.repository.chat_repo import ChatRepository
from app.services.coach_service import CoachService
from app.services.statistics_service import StatisticsService


class FakeLLMProvider:
    def __init__(self):
        self.history_messages = []

    async def send_message(self, messages: list[dict[str, str]]) -> str:
        self.history_messages.append(messages)
        return "Ответ LLM"


class BrokenFakeLLMProvider:
    def __init__(self):
        self.history_messages = []

    async def send_message(self, messages: list[dict[str, str]]) -> str:
        self.history_messages.append(messages)
        raise AIProviderNotAvailable


@pytest.fixture
def make_coach_service(db_test_session, get_fake_statistic_service):
    def _create_coach_service(
        *, llm_provider: LLMProvider | None = None, stat_service: StatisticsService | None = None
    ) -> CoachService:
        return CoachService(
            chat_repo=ChatRepository(session=db_test_session),
            llm_provider=llm_provider or FakeLLMProvider(),
            stat_service=stat_service or get_fake_statistic_service,
        )

    return _create_coach_service
