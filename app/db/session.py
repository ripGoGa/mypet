from sqlmodel import SQLModel, Session, create_engine

from app.core.config import db_settings

engine = create_engine(db_settings.database_url, echo=True, connect_args=db_settings.engine_connect_args)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
