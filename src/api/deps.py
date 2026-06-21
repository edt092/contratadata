"""Dependencias compartidas — engine SQLAlchemy y sesión de DB."""

import os
from functools import lru_cache

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

load_dotenv()


@lru_cache(maxsize=1)
def _engine():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL no está configurada.")
    return create_engine(url, pool_pre_ping=True, future=True)


@lru_cache(maxsize=1)
def _session_factory():
    return sessionmaker(bind=_engine(), autocommit=False, autoflush=False)


def get_db():
    db: Session = _session_factory()()
    try:
        yield db
    finally:
        db.close()
