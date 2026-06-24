from typing import Protocol


class LLMProvider(Protocol):
    async def send_message(self, messages: list[dict[str, str]]) -> str:
        """"Принимает текст по ролям и возвращает ответ от ИИ"""
