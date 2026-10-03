from sqlmodel import create_engine, Session
from app.core.config import get_settings
from functools import lru_cache

@lru_cache
def get_engine():
    return create_engine(get_settings().sqlalchemy_url)