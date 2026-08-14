from datetime import UTC, datetime, timedelta
from typing import Sequence

from sqlmodel import Session, select

from app.models.models import ChatMessage


class ChatRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_chat_history(self, user_id: int) -> Sequence[ChatMessage]:
        week_ago = datetime.now(UTC) - timedelta(days=7)
        messages = self.session.exec(select(ChatMessage).where(ChatMessage.user_id == user_id).where(
            ChatMessage.created_at >= week_ago)).all()
        return messages

    def save_message(self, message: ChatMessage) -> ChatMessage:
        self.session.add(message)
        self.session.flush()
        return message

    def commit(self):
        self.session.commit()

    def get_all_chat_history(self, user_id: int) -> Sequence[ChatMessage]:
        messages = self.session.exec(select(ChatMessage).where(ChatMessage.user_id == user_id)).all()
        return messages



