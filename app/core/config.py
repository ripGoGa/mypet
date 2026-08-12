from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent.parent  # корень проекта


class DatabaseSettings:
    database_url: str = f'sqlite:///{BASE_DIR}/data/app.db'
    engine_connect_args: dict = {'check_same_thread': False}


db_settings = DatabaseSettings()


class KeySettings(BaseSettings):
    secret_key: str

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


key_settings = KeySettings()
