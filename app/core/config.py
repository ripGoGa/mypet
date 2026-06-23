from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent  # корень проекта


class DatabaseSettings:
    database_url: str = f'sqlite:///{BASE_DIR}/data/app.db'
    engine_connect_args: dict = {'check_same_thread': False}


db_settings = DatabaseSettings()
