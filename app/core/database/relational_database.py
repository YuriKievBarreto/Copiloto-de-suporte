from sqlmodel import create_engine, Session, SQLModel
from app.core.config import get_settings
from functools import lru_cache
from app import models

@lru_cache
def get_engine():
    return create_engine(get_settings().sqlalchemy_url)


def create_tables():
    engine = get_engine()
    SQLModel.metadata.create_all(engine)

