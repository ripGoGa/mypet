from datetime import datetime, timedelta
from typing import Sequence

from sqlalchemy import select
from sqlmodel import Session

from app.models.models import ChatMessage


class ChatRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_chat_history(self, user_id: int) -> Sequence[ChatMessage]:
        week_ago = datetime.now() - timedelta(days=7)
        messages = self.session.exec(select(ChatMessage).where(ChatMessage.user_id == user_id).where(
            ChatMessage.created_at >= week_ago)).all()
        return messages

    def save_message(self, message: ChatMessage) -> ChatMessage:
        self.session.add(message)
        self.session.flush()
        return message
