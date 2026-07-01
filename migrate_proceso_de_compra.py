"""Migración one-off: agrega proceso_de_compra y recrea uq_contract_idempotent
sobre (fuente, proceso_de_compra) en vez de (fuente, entity_id, supplier_id, valor, fecha).

Ejecutar una sola vez contra la base de producción antes de desplegar el
pipeline con la nueva lógica de upsert (DO UPDATE en vez de DO NOTHING):

    python migrate_proceso_de_compra.py

Es idempotente: puede correrse más de una vez sin error. Las filas cargadas
antes de este cambio quedan con proceso_de_compra=NULL (Postgres no compara
NULLs como iguales, así que no violan la unique constraint) y no se tocan;
solo las próximas corridas incrementales usan la nueva clave.
"""

import logging
import os

from dotenv import load_dotenv
from sqlalchemy import text

from src.load.loader import get_engine

load_dotenv()
logging.basicConfig(level="INFO", format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("migrate")


def run() -> None:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise EnvironmentError("DATABASE_URL no está configurada.")

    engine = get_engine(database_url)
    with engine.begin() as conn:
        conn.execute(text(
            "ALTER TABLE contracts ADD COLUMN IF NOT EXISTS proceso_de_compra VARCHAR(150)"
        ))
        logger.info("Columna proceso_de_compra verificada/creada.")

        conn.execute(text(
            "ALTER TABLE contracts DROP CONSTRAINT IF EXISTS uq_contract_idempotent"
        ))
        conn.execute(text(
            "ALTER TABLE contracts ADD CONSTRAINT uq_contract_idempotent "
            "UNIQUE (fuente, proceso_de_compra)"
        ))
        logger.info(
            "Constraint uq_contract_idempotent recreada sobre (fuente, proceso_de_compra)."
        )

    logger.info("Migración completada.")


if __name__ == "__main__":
    run()
