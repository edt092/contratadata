"""Migración one-off: crea la tabla `feedback` para el flujo de user testing
(ver testing.md) — feedback de usuarios sin login, con créditos premium
opcionales para quien deje su email.

Ejecutar una sola vez contra la base de producción:

    python migrate_add_feedback_table.py

Es idempotente: usa Base.metadata.create_all, que no toca tablas existentes.
"""

import logging
import os

from dotenv import load_dotenv

from src.load.loader import get_engine
from src.load.models import Base

load_dotenv()
logging.basicConfig(level="INFO", format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("migrate")


def run() -> None:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise EnvironmentError("DATABASE_URL no está configurada.")

    engine = get_engine(database_url)

    Base.metadata.create_all(engine, tables=[Base.metadata.tables["feedback"]])
    logger.info("Tabla 'feedback' verificada/creada.")


if __name__ == "__main__":
    run()
