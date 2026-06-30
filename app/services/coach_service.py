from pathlib import Path
from datetime import date
from app.core.exceptions import DownloadPromptError
from app.infrastructure.llm.llm_protocol import LLMProvider
from app.models.models import ChatMessage, AthleteProfile, Users
from app.repository.chat_repo import ChatRepository
from app.repository.workout_repo import WorkoutRepository
from app.services.stats_calculator import StatsCalculator


class CoachService:
    def __init__(self, workout_repo: WorkoutRepository, chat_repo: ChatRepository, llm_provider: LLMProvider):
        self.workout_repo = workout_repo
        self.llm_provider = llm_provider
        self.system_prompt = self._load_prompt('System_Persona.txt')
        self.user_profile = self._load_prompt('User_Profile.txt')
        self.current_content = self._load_prompt('Current_Content.txt')
        self.chat_repo = chat_repo

    @staticmethod
    def _load_prompt(filename: str) -> str:
        current_file = Path(__file__)
        prompt_path = current_file.parent.parent / 'prompts' / filename
        try:
            return prompt_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f'Ошибка загрузки промта: {e}')
            raise DownloadPromptError

    async def generate_coach_response(self, user_message: str, user: Users) -> str:
        # Собираем данные
        athlete_data = self._build_athlete_data(user)
        workout_sum = self._build_workouts(user)
        chat_history = self._build_chat_history(user)

        # Собираем финальный промпт

        profile_section = self.user_profile.format(**athlete_data)
        content_section = self.current_content.format(current_data=date.today().isoformat(),
                                                      recent_workouts_summary=workout_sum,
                                                      user_message=user_message)
        system_content = f'{self.system_prompt}\n\n{profile_section}'
        messages = [
            {"role": "system", "content": system_content},
            *chat_history,
            {"role": "user", "content": content_section}
        ]
        # Отправляем в сообщение в ИИ-провайдер
        ai_response = await self.llm_provider.send_message(messages)
        self.chat_repo.save_message(ChatMessage(user_id=user.id, role='user', content=user_message))
        self.chat_repo.save_message(ChatMessage(user_id=user.id, role='assistant', content=ai_response))
        self.chat_repo.commit()
        return ai_response

    def _build_athlete_data(self, user: Users) -> dict:
        # Объединяем данные отлета в один словарь для промпта
        athlete_data = user.athlete_profile.model_dump()
        athlete_data.update(user.user_profile.model_dump())

        # Проверяем на None
        for key, value in athlete_data.items():
            if value is None:
                athlete_data[key] = 'Не указано'
        return athlete_data

    def _build_workouts(self, user: Users) -> str:
        # Достаем тренировки за неделю
        workouts = self.workout_repo.get_statistic_workouts(user_id=user.id, period=7)

        # Собираем статистику
        stats_workouts = StatsCalculator(workouts)
        work_sum = 'Статистика тренировок за 7 дней'
        if not workouts:
            work_sum = 'Тренировок пока нет'
        else:
            work_sum += (f'\n -Общий километраж: {stats_workouts.raw_total_distance}\n '
                         f'-Суммарный тренировочный стресс (TSS): {stats_workouts.total_tss_num}\n'
                         f'-Общее время в движении: {stats_workouts.total_moving_time}\n\n'
                         f'Распределение нагрузки:\n'
                         f'-Тяжёлые тренировки: {stats_workouts.hard_count}\n'
                         f'-Средние тренировки: {stats_workouts.medium_count}\n'
                         f'-Легкие тренировки: {stats_workouts.light_count}\n')
        return work_sum

    def _build_chat_history(self, user: Users) -> list[dict]:
        recent_msgs = self.chat_repo.get_chat_history(user_id=user.id)
        result = []
        for m in recent_msgs:
            message_dict = dict(role=m.role, content=m.content)
            result.append(message_dict)
        return result
