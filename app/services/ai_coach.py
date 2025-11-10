import httpx
from typing import List, Optional
from fastapi import HTTPException


class OllamaService:
    """Сервис для работы с Ollama API"""
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = "llama3.1"

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
                        "stream": True,  # Без потоковой передачи
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

    def format_workouts(self, workouts: List) -> str:
        """
        Форматирует список тренировок в текст для промпта

        Args:
            workouts: Список объектов Workout

        Returns:
            Текстовое представление тренировок
        """
        # TODO: Преобразовать тренировки в читаемый текст
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
        """
        Получает рекомендации от ИИ-тренера

        Args:
            profile: Объект UserProfile
            workouts: Список последних тренировок

        Returns:
            Рекомендации от ИИ
        """
        # TODO: Собрать промпт и вызвать generate()
        pass
