from datetime import date
import httpx
from typing import List
from fastapi import HTTPException
from app.models.models import ChatMessage, AthleteProfile
from pathlib import Path


def get_ollama_service():
    return OllamaService()


class OllamaService:
    """Сервис для работы с Ollama API"""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = "llama3.1"
        self.system_prompt = self._load_prompt('System_Persona.txt')
        self.user_profile = self._load_prompt('User_Profile.txt')
        self.current_content = self._load_prompt('Current_Content.txt')

    @staticmethod
    def _load_prompt(filename: str) -> str:
        current_file = Path(__file__)
        prompt_path = current_file.parent.parent / 'prompts' / filename
        try:
            return prompt_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f'Ошибка загрузки промта: {e}')
            return 'Произошла ошибка файл промпта не найден'

    async def generate(self, prompt: str, timeout: int = 60) -> str:
        """Отправляет промпт в Ollama и возвращает ответ модели """
        try:
            # Создаём асинхронный HTTP-клиент с таймаутом
            async with httpx.AsyncClient(timeout=timeout) as client:
                # Отправляем POST-запрос к Ollama API
                response = await client.post(
                    f"{self.base_url}/api/generate",  # URL эндпоинта
                    json={
                        "model": self.model,  # Название модели
                        "prompt": prompt,  # Промпт для модели
                        "stream": False,  # Без потоковой передачи
                        "options": {
                            "num_ctx": 8192  # Контекстное окно 8k
                        }
                    }
                )
                # Проверяем, что запрос успешен (код 200)
                response.raise_for_status()
                # Парсим JSON-ответ
                data = response.json()
                # Извлекаем текст ответа модели
                return data.get("response", "")
        except httpx.ConnectError:
            # Ollama не запущен или недоступен
            raise HTTPException(
                status_code=503,
                detail="Сервис ИИ недоступен. Убедитесь, что Ollama запущен."
            )
        except httpx.TimeoutException:
            # Превышено время ожидания
            raise HTTPException(
                status_code=504,
                detail="Превышено время ожидания ответа от ИИ."
            )
        except Exception as e:
            # Любая другая ошибка
            print(f"Ошибка при вызове Ollama: {e}")
            raise HTTPException(
                status_code=500,
                detail="Внутренняя ошибка при обращении к ИИ."
            )

    @staticmethod
    def format_workouts(workouts: List) -> str:
        """Форматирует список тренировок в текст для промпта
        Args:
            workouts: Список объектов Workout
        Returns:
            Текстовое представление тренировок
        """
        if not workouts:
            return 'Тренировок пока нет'
        result = f'Последние {len(workouts)} тренировок: \n\n'
        for i, workout in enumerate(workouts, 1):
            line = (f'{i}. '
                    f'{workout.distance_km} км'
                    f'{workout.duration}, '
                    f'TSS {workout.training_stress_score}, '
                    f'{workout.avg_watts} Вт (NP {workout.normalized_power} ВТ, IF {workout.intensity_factor})')
            if workout.avg_heartrate:
                line += f', {workout.avg_heartrate} уд/мин'
            if workout.avg_cadence:
                line += f', {workout.avg_cadence} об/мин'
            result += line + '\n'
        return result

    async def get_training_advice(self, profile, workouts: List) -> str:
        """Получает рекомендации от ИИ-тренера
        Args:
            profile: Объект UserProfile
            workouts: Список последних тренировок
        Returns:
            Рекомендации от ИИ
        """
        result = self.format_workouts(workouts)
        if result == 'Тренировок пока нет':
            return 'Тренировок пока нет'
        ftp = profile.ftp
        weight_kg = profile.weight_kg
        prompt = (f'Ты опытный тренер по велоспорту и должен дать рекомендации для следующей тренировки,'
                  f' а так же составь список тренировок на неделю. Вот мои '
                  f'данные: мой FTP: {ftp}, 'f'вес: {weight_kg}. Вот мой список тренировок:')
        prompt += result
        advice = await self.generate(prompt)
        return advice

    async def chat(self, messages: List[dict], timeout: int = 60) -> str:
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(f"{self.base_url}/api/chat", json={'model': self.model,
                                                                                'messages': messages, 'stream': False,
                                                                                'options': {'num_ctx': 8192}})
            response.raise_for_status()
            data = response.json()
            return data.get('message', {}).get('content', "")

        except httpx.ConnectError:
            raise HTTPException(503, detail='Сервис ИИ не доступен')
        except httpx.TimeoutException:
            raise HTTPException(504, detail='Превышено время ожидания')
        except Exception as e:
            print(f'Ошибка Chat: {e}')
            raise HTTPException(500, detail='Внутренняя ошибка ИИ')

    async def get_chat_response(self, history: List['ChatMessage'], user_question: str):
        system_instruction = self.system_prompt.format(sport='cycling')
        message_list = [{'role': 'system', 'content': system_instruction}]

        for msg in history:
            message_list.append({'role': msg.role, 'content': msg.content})
        message_list.append({'role': 'user', 'content': user_question})

        return await self.chat(message_list)

    async def build_chat_messages(self, user_profile, athlete_profile, user_message, summary, message_history):
        # Достаем данные атлета
        # Объединяем данные
        athlete_data = user_profile.model_dump()
        if athlete_profile:
            athlete_data.update(athlete_profile.model_dump())

        # Проверка на None
        for key, value in athlete_data.items():
            if value is None:
                athlete_data[key] = "Не указано"

        # Формируем историю
        history_text = self.format_history(message_history)

        # Заполняем шаблоны
        profile_section = self.user_profile.format(**athlete_data)
        content_section = self.current_content.format(current_date=date.today().isoformat(),
                                                      recent_workouts_summary=summary,
                                                      user_message=user_message)
        # Собираем все вместе
        user_prompt = f'{profile_section}\n\n{history_text}\n\n{content_section}'

        return [{'role': 'system', 'content': self.system_prompt},
                {'role': 'user', 'content': user_prompt}]

    def format_history(self, history: List[ChatMessage]) -> str:
        # Берем последние 10 объектов
        recent_msgs = history[-10:]
        result = '### ПРЕДЫДУЩИЕ СООБЩЕНИЯ\n'
        # Перебираем последние сообщения
        for mess in recent_msgs:
            dump_mess = mess.model_dump(include={'role', 'content'})
            result += f'{dump_mess["role"]}: {dump_mess["content"]}\n'
        return result
