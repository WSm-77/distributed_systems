from typing import Annotated

from fastapi import Depends
from sqlmodel import SQLModel, Session, create_engine

from config.config import CONFIG

connect_args = {}
if CONFIG.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(CONFIG.database_url, connect_args=connect_args)


def get_session():
    with Session(engine) as session:
        yield session


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


SessionDep = Annotated[Session, Depends(get_session)]
