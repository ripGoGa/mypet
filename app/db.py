from pathlib import Path
from sqlmodel import SQLModel, Session, create_engine

DB_PATH = Path('data/app.db')
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

DATABASE_URL = f'sqlite:///{DB_PATH}'
engine = create_engine(DATABASE_URL, echo=True, connect_args={'check_same_thread': False})


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
