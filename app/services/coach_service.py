from pathlib import Path

from app.core.exceptions import DownloadPromptError
from app.infrastructure.llm.llm_protocol import LLMProvider
from app.repository.workout_repo import WorkoutRepository


class CoachService:
    def __init__(self, repo: WorkoutRepository, llm_provider: LLMProvider):
        self.repo = repo
        self.llm_provider = llm_provider
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
            raise DownloadPromptError
