"""Migración one-off: tablas de autenticación Auth0 (ver auth.md) —
app_users, subscriptions, premium_entitlements — y agrega la columna
'user_id' (nullable) a premium_leads para vincular leads autenticados.

Reemplaza el modelo anterior de acceso premium por email (premium_users, ver
scalability.md) por identidad real vía Auth0 + plan en Neon. La tabla vieja
'premium_users' NO se borra automáticamente acá (queda vacía y sin uso, pero
borrarla es una operación destructiva que se deja aparte, ver el bloque
comentado al final).

Ejecutar una sola vez contra la base de producción:

    python migrate_add_auth_tables.py

Es idempotente: create_all para tablas nuevas, y el ALTER de premium_leads
comprueba si la columna ya existe antes de agregarla.
"""

import logging
import os

from dotenv import load_dotenv
from sqlalchemy import inspect, text

from src.load.loader import get_engine
from src.load.models import Base

load_dotenv()
logging.basicConfig(level="INFO", format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("migrate")

NEW_TABLES = ["app_users", "subscriptions", "premium_entitlements"]


def run() -> None:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise EnvironmentError("DATABASE_URL no está configurada.")

    engine = get_engine(database_url)

    Base.metadata.create_all(engine, tables=[Base.metadata.tables[t] for t in NEW_TABLES])
    logger.info("Tablas verificadas/creadas: %s", ", ".join(NEW_TABLES))

    inspector = inspect(engine)
    existing_cols = {c["name"] for c in inspector.get_columns("premium_leads")}
    if "user_id" not in existing_cols:
        with engine.begin() as conn:
            conn.execute(text(
                "ALTER TABLE premium_leads "
                "ADD COLUMN user_id INTEGER REFERENCES app_users(id)"
            ))
        logger.info("premium_leads.user_id agregada.")
    else:
        logger.info("premium_leads.user_id ya existía.")

    logger.info("Migración completada.")


if __name__ == "__main__":
    run()


# ── Limpieza opcional (no se ejecuta automáticamente) ────────────────────────
# La tabla 'premium_users' del modelo anterior (email-based, ver
# scalability.md) queda sin uso tras esta migración. Verificar que está vacía
# y borrarla a mano si se quiere:
#
#     python -c "
#     from src.load.loader import get_engine
#     from sqlalchemy import text
#     import os
#     from dotenv import load_dotenv; load_dotenv()
#     engine = get_engine(os.getenv('DATABASE_URL'))
#     with engine.begin() as conn:
#         count = conn.execute(text('SELECT count(*) FROM premium_users')).scalar_one()
#         print('filas en premium_users:', count)
#         if count == 0:
#             conn.execute(text('DROP TABLE premium_users'))
#             print('premium_users eliminada.')
#     "
