import httpx

from app.core.exceptions import AIProvideInternalError, AIProviderNotAvailable, AIProviderTimeOut


class OllamaProvider:
    """"Провайдер для использования ИИ"""

    def __init__(self, base_url: str = "http://localhost:11434", num_ctx: int = 8192):
        self.base_url = base_url
        self.model = 'llama3.1'
        self.num_ctx = num_ctx
        self.timeout = 60

    async def send_message(self, messages: list[dict[str, str]]) -> str:
        """"Принимает текст по ролям и возвращает ответ от ИИ"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f'{self.base_url}/api/chat', json={'model': self.model,
                                                                                'messages': messages,
                                                                                'stream': False,
                                                                                'options': {'num_ctx': 8192}})
                response.raise_for_status()
                data = response.json()
                return data.get('message', {}).get('content', '')
        except httpx.ConnectError:
            raise AIProviderNotAvailable
        except httpx.TimeoutException:
            raise AIProviderTimeOut
        except Exception as e:
            print(f'Ошибка Chat: {e}')
            raise AIProvideInternalError
