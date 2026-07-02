"""Migración one-off: dedupe suppliers por nombre y agrega uq_supplier_nombre.

Necesaria antes de desplegar la carga masiva de load_batch (src/load/loader.py),
que usa INSERT ... ON CONFLICT DO NOTHING sobre suppliers.nombre — eso requiere
una unique constraint en esa columna, que la tabla original no tenía.

Ejecutar una sola vez contra la base de producción:

    python migrate_supplier_unique.py

Es idempotente: si ya no hay duplicados y la constraint ya existe, no hace nada.
Para cada nombre duplicado conserva el id más antiguo (MIN(id)), reasigna
contracts.supplier_id de los duplicados hacia ese id, y borra las filas sobrantes.
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
        dup_count = conn.execute(text(
            "SELECT count(*) FROM ("
            "  SELECT nombre FROM suppliers GROUP BY nombre HAVING count(*) > 1"
            ") d"
        )).scalar()
        logger.info("Nombres de proveedor duplicados encontrados: %d", dup_count)

        if dup_count:
            conn.execute(text("""
                WITH keepers AS (
                    SELECT nombre, MIN(id) AS keep_id
                    FROM suppliers
                    GROUP BY nombre
                ),
                remap AS (
                    SELECT s.id AS dup_id, k.keep_id
                    FROM suppliers s
                    JOIN keepers k ON k.nombre = s.nombre
                    WHERE s.id <> k.keep_id
                )
                UPDATE contracts c
                SET supplier_id = r.keep_id
                FROM remap r
                WHERE c.supplier_id = r.dup_id
            """))
            logger.info("Contratos reapuntados a los proveedores conservados.")

            conn.execute(text("""
                WITH keepers AS (
                    SELECT nombre, MIN(id) AS keep_id
                    FROM suppliers
                    GROUP BY nombre
                )
                DELETE FROM suppliers s
                USING keepers k
                WHERE s.nombre = k.nombre AND s.id <> k.keep_id
            """))
            logger.info("Filas de proveedores duplicadas eliminadas.")

        conn.execute(text(
            "ALTER TABLE suppliers DROP CONSTRAINT IF EXISTS uq_supplier_nombre"
        ))
        conn.execute(text(
            "ALTER TABLE suppliers ADD CONSTRAINT uq_supplier_nombre UNIQUE (nombre)"
        ))
        logger.info("Constraint uq_supplier_nombre creada sobre suppliers.nombre.")

    logger.info("Migración completada.")


if __name__ == "__main__":
    run()
