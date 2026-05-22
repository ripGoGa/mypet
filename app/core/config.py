class DatabaseSettings:
    database_url: str = 'sqlite:///data/app.db'
    engine_connect_args: dict = {'check_same_thread': False}


db_settings = DatabaseSettings()
