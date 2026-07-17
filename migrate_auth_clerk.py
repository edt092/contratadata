"""Migración aditiva: Auth0 → Clerk (ver auth2.md FASE 2).

Agrega las columnas necesarias para identificar usuarios por proveedor
(auth_provider/auth_provider_user_id) en vez de solo auth0_sub, y agrega
user_id a saved_alerts/competitor_watchlist para que dejen de depender de
user_email. No borra ni renombra nada existente — auth0_sub y user_email
se conservan hasta que cleanup_auth0_columns.py confirme que ya no hacen
falta.

Idempotente: cada ALTER comprueba si la columna/constraint ya existe antes
de aplicarla. Ejecutar una sola vez contra la base de producción:

    python migrate_auth_clerk.py

Antes de correr esto contra producción: crear un branch de Neon (backup
instantáneo y reversible) — ver docs/clerk-setup.md.

Rollback (si hace falta revertir esta migración, no el cleanup):

    ALTER TABLE app_users DROP CONSTRAINT IF EXISTS uq_app_user_provider_identity;
    ALTER TABLE app_users DROP COLUMN IF EXISTS auth_provider;
    ALTER TABLE app_users DROP COLUMN IF EXISTS auth_provider_user_id;
    ALTER TABLE saved_alerts DROP COLUMN IF EXISTS user_id;
    ALTER TABLE competitor_watchlist DROP CONSTRAINT IF EXISTS uq_competitor_watch_userid_supplier;
    ALTER TABLE competitor_watchlist DROP COLUMN IF EXISTS user_id;

No es destructivo: auth0_sub y user_email nunca se tocan acá.
"""

import logging
import os

from dotenv import load_dotenv
from sqlalchemy import inspect, text

from src.load.loader import get_engine

load_dotenv()
logging.basicConfig(level="INFO", format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("migrate_auth_clerk")


def _add_column_if_missing(conn, inspector, table: str, column: str, ddl: str) -> None:
    existing = {c["name"] for c in inspector.get_columns(table)}
    if column in existing:
        logger.info("%s.%s ya existía.", table, column)
        return
    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {ddl}"))
    logger.info("%s.%s agregada.", table, column)


def _add_unique_constraint_if_missing(conn, inspector, table: str, name: str, columns: str) -> None:
    existing = {c["name"] for c in inspector.get_unique_constraints(table)}
    if name in existing:
        logger.info("Constraint %s ya existía.", name)
        return
    conn.execute(text(f"ALTER TABLE {table} ADD CONSTRAINT {name} UNIQUE ({columns})"))
    logger.info("Constraint %s agregada.", name)


def run() -> None:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise EnvironmentError("DATABASE_URL no está configurada.")

    engine = get_engine(database_url)
    inspector = inspect(engine)

    with engine.begin() as conn:
        # ── app_users: identidad por proveedor ──────────────────────────────
        _add_column_if_missing(conn, inspector, "app_users", "auth_provider", "auth_provider VARCHAR(30)")
        _add_column_if_missing(
            conn, inspector, "app_users", "auth_provider_user_id", "auth_provider_user_id VARCHAR(255)"
        )
        _add_column_if_missing(
            conn, inspector, "app_users", "is_active", "is_active BOOLEAN NOT NULL DEFAULT true"
        )

        backfilled = conn.execute(text(
            "UPDATE app_users SET auth_provider = 'auth0', auth_provider_user_id = auth0_sub "
            "WHERE auth_provider IS NULL AND auth0_sub IS NOT NULL"
        ))
        logger.info("app_users backfilled desde auth0_sub: %d filas.", backfilled.rowcount)

    # Constraint UNIQUE aparte: falla si el backfill dejó duplicados, y
    # queremos ver ese error específico en vez de que aborte el resto.
    inspector = inspect(engine)
    with engine.begin() as conn:
        _add_unique_constraint_if_missing(
            conn, inspector, "app_users", "uq_app_user_provider_identity", "auth_provider, auth_provider_user_id"
        )

    # ── saved_alerts / competitor_watchlist: propiedad por user_id ──────────
    inspector = inspect(engine)
    with engine.begin() as conn:
        _add_column_if_missing(conn, inspector, "saved_alerts", "user_id", "user_id INTEGER REFERENCES app_users(id)")
        _add_column_if_missing(
            conn, inspector, "competitor_watchlist", "user_id", "user_id INTEGER REFERENCES app_users(id)"
        )

        for table in ("saved_alerts", "competitor_watchlist"):
            result = conn.execute(text(
                f"UPDATE {table} t SET user_id = u.id "
                f"FROM app_users u "
                f"WHERE t.user_id IS NULL AND lower(trim(t.user_email)) = lower(trim(u.email))"
            ))
            logger.info("%s.user_id backfilled: %d filas.", table, result.rowcount)

    # NULL != NULL en Postgres: agregar esta UNIQUE con user_id todavía
    # nullable es seguro (múltiples filas sin vincular no colisionan).
    inspector = inspect(engine)
    with engine.begin() as conn:
        _add_unique_constraint_if_missing(
            conn, inspector, "competitor_watchlist", "uq_competitor_watch_userid_supplier", "user_id, supplier_name"
        )

    # ── Reporte de filas sin vincular o ambiguas (no falla la migración) ────
    with engine.connect() as conn:
        for table in ("saved_alerts", "competitor_watchlist"):
            unmatched = conn.execute(text(
                f"SELECT id, user_email FROM {table} WHERE user_id IS NULL"
            )).all()
            if unmatched:
                logger.warning(
                    "%s: %d filas sin user_id (sin AppUser con ese email — revisar antes del cleanup): %s",
                    table, len(unmatched), [(r.id, r.user_email) for r in unmatched],
                )
            else:
                logger.info("%s: todas las filas quedaron vinculadas a un user_id.", table)

        ambiguous = conn.execute(text(
            "SELECT lower(trim(email)) AS norm_email, count(*) "
            "FROM app_users WHERE email IS NOT NULL "
            "GROUP BY lower(trim(email)) HAVING count(*) > 1"
        )).all()
        if ambiguous:
            logger.warning("Emails ambiguos en app_users (más de un usuario): %s", list(ambiguous))
        else:
            logger.info("Sin emails ambiguos en app_users.")

    logger.info("Migración completada.")


if __name__ == "__main__":
    run()
