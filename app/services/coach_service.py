from datetime import date
from pathlib import Path
from typing import Sequence

from app.core.exceptions import DownloadPromptError
from app.core.formatter import format_pace, format_stats, format_time
from app.infrastructure.llm.llm_protocol import LLMProvider
from app.models.models import ChatMessage, Users
from app.repository.chat_repo import ChatRepository
from app.services.statistics_service import StatisticsService


class CoachService:
    def __init__(
        self,
        chat_repo: ChatRepository,
        llm_provider: LLMProvider,
        stat_service: StatisticsService,
    ):
        self.llm_provider = llm_provider
        self.system_prompt = self._load_prompt("System_Persona.txt")
        self.user_profile = self._load_prompt("User_Profile.txt")
        self.current_content = self._load_prompt("Current_Content.txt")
        self.chat_repo = chat_repo
        self.stat_service = stat_service

    @staticmethod
    def _load_prompt(filename: str) -> str:
        current_file = Path(__file__)
        prompt_path = current_file.parent.parent / "prompts" / filename
        try:
            return prompt_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Ошибка загрузки промта: {e}")
            raise DownloadPromptError

    async def generate_coach_response(self, user_message: str, user: Users) -> str:
        # Собираем данные
        athlete_data = self._build_athlete_data(user)
        workout_sum = self._build_workouts(user)
        chat_history = self._build_chat_history(user)

        # Собираем финальный промпт

        profile_section = self.user_profile.format(**athlete_data)
        content_section = self.current_content.format(
            current_date=date.today().isoformat(),
            recent_workouts_summary=workout_sum,
            user_message=user_message,
        )
        system_content = f"{self.system_prompt}\n\n{profile_section}"
        messages = [
            {"role": "system", "content": system_content},
            *chat_history,
            {"role": "user", "content": content_section},
        ]
        # Отправляем в сообщение в ИИ-провайдер
        ai_response = await self.llm_provider.send_message(messages)
        self.chat_repo.save_message(ChatMessage(user_id=user.id, role="user", content=user_message))
        self.chat_repo.save_message(ChatMessage(user_id=user.id, role="assistant", content=ai_response))
        self.chat_repo.commit()
        return ai_response

    @staticmethod
    def _build_athlete_data(user: Users) -> dict:
        # Объединяем данные отлета в один словарь для промпта
        athlete_data = user.athlete_profile.model_dump()
        athlete_data.update(user.user_profile.model_dump())

        # Проверяем на None
        for key, value in athlete_data.items():
            if value is None:
                athlete_data[key] = "Не указано"
        return athlete_data

    def _build_workouts(self, user: Users, period: int = 7) -> str:
        # Достаем тренировки за неделю
        cycling_stats = self.stat_service.get_cycling_stats(user_id=user.id, period=period)
        running_stats = self.stat_service.get_running_stats(user_id=user.id, period=period)

        # Собираем саммари по видам спорта
        final_prompt = []
        if cycling_stats.count_workouts > 0:
            blocks = [
                f"Статистика вело тренировок за {period} дней",
                f"-Общий километраж: {format_stats(cycling_stats.raw_total_distance, 'км.')}",
                f"-Суммарный тренировочный стресс (TSS): {format_stats(cycling_stats.total_tss_num)}",
                f"-Общее время в движении: {format_time(cycling_stats.total_moving_time)}",
                f"-Средние ватты: {format_stats(cycling_stats.avg_watts_num, 'Вт.')}",
                f"-Средний пульс: {format_stats(cycling_stats.avg_heartrate_num, 'уд/мин')}",
                f"-Средний каданс: {format_stats(cycling_stats.avg_cadence_num, 'об./мин')}",
                f"-Максимальный IF: {format_stats(cycling_stats.max_in_factor)}",
                "Распределение нагрузки:",
                f"-Тяжёлые тренировки: {cycling_stats.hard_count}",
                f"-Средние тренировки: {cycling_stats.medium_count}",
                f"-Легкие тренировки: {cycling_stats.light_count}",
                f"-Всего тренировок: {cycling_stats.count_workouts}",
            ]
            final_prompt.append("\n".join(blocks))

        if running_stats.count_workouts > 0:
            blocks = [
                f"Статистика беговых тренировок за {period} дней",
                f"-Общий километраж: {format_stats(running_stats.total_distance, 'км')}",
                f"-Общее время бега: {format_time(running_stats.total_moving_time)}",
                f"-Средний каданс: {format_stats(running_stats.avg_cadence_num, 'шагов/мин')}",
                f"-Средний темп: {format_pace(running_stats.avg_speed_num)}",
                f"-Средний пульс: {format_stats(running_stats.avg_heartrate_num, 'уд/мин')}",
                f"-Максимальная дистанция: {format_stats(running_stats.max_distance, 'км')}",
                f"-Всего тренировок: {running_stats.count_workouts}",
            ]
            final_prompt.append("\n".join(blocks))

        return "\n\n".join(final_prompt) if final_prompt else "Тренировки не найдены."

    def _build_chat_history(self, user: Users) -> list[dict]:
        recent_msgs = self.chat_repo.get_chat_history(user_id=user.id)
        result = []
        for m in recent_msgs:
            message_dict = dict(role=m.role, content=m.content)
            result.append(message_dict)
        return result

    def get_chat_history(self, user_id: int) -> Sequence[ChatMessage]:
        return self.chat_repo.get_all_chat_history(user_id)
