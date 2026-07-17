"""Limpieza posterior al corte Auth0 → Clerk (ver auth2.md FASE 2/7).

NO ejecutar automáticamente como parte del deploy. Correr a mano días
después del corte a Clerk, solo cuando:

  1. migrate_auth_clerk.py ya corrió y no reportó filas sin vincular ni
     emails ambiguos (o esas filas se resolvieron a mano).
  2. Todo el tráfico real ya pasó por el flujo de Clerk al menos una vez
     (GET /api/me sincroniza auth_provider_user_id) — confirmar que no
     queden app_users con auth_provider IS NULL que sigan iniciando sesión.
  3. Se tomó un branch de Neon nuevo (esto SÍ borra columnas — ver
     docs/clerk-setup.md para el comando de backup).

Qué hace:
  - saved_alerts.user_id / competitor_watchlist.user_id → NOT NULL.
  - Elimina la columna user_email de ambas tablas y la constraint UNIQUE
    vieja (user_email, supplier_name) de competitor_watchlist.
  - Elimina app_users.auth0_sub.

Uso:
    python cleanup_auth0_columns.py --dry-run   # solo reporta, no aplica nada
    python cleanup_auth0_columns.py --apply      # aplica los cambios

Rollback: estas operaciones son destructivas (DROP COLUMN) — el único
rollback real es restaurar desde el branch de Neon tomado en el paso 3.
"""

import argparse
import logging
import os

from dotenv import load_dotenv
from sqlalchemy import text

from src.load.loader import get_engine

load_dotenv()
logging.basicConfig(level="INFO", format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("cleanup_auth0_columns")


def _check_ready(conn) -> bool:
    ok = True
    for table in ("saved_alerts", "competitor_watchlist"):
        n = conn.execute(text(f"SELECT count(*) FROM {table} WHERE user_id IS NULL")).scalar_one()
        if n:
            logger.error("%s: %d filas todavía sin user_id — no se puede continuar.", table, n)
            ok = False
    n = conn.execute(text(
        "SELECT count(*) FROM app_users WHERE auth_provider IS NULL OR auth_provider_user_id IS NULL"
    )).scalar_one()
    if n:
        logger.error("app_users: %d filas sin auth_provider/auth_provider_user_id — no se puede continuar.", n)
        ok = False
    return ok


def run(apply: bool) -> None:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise EnvironmentError("DATABASE_URL no está configurada.")

    engine = get_engine(database_url)

    with engine.connect() as conn:
        ready = _check_ready(conn)

    if not ready:
        logger.error("Cleanup abortado: resolver las filas reportadas arriba antes de reintentar.")
        return

    if not apply:
        logger.info("Dry-run OK: todo está listo para el cleanup. Volver a correr con --apply.")
        return

    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE saved_alerts ALTER COLUMN user_id SET NOT NULL"))
        conn.execute(text("ALTER TABLE competitor_watchlist ALTER COLUMN user_id SET NOT NULL"))

        conn.execute(text(
            "ALTER TABLE competitor_watchlist "
            "DROP CONSTRAINT IF EXISTS uq_competitor_watch_user_supplier"
        ))
        conn.execute(text("ALTER TABLE saved_alerts DROP COLUMN IF EXISTS user_email"))
        conn.execute(text("ALTER TABLE competitor_watchlist DROP COLUMN IF EXISTS user_email"))
        conn.execute(text("ALTER TABLE app_users DROP COLUMN IF EXISTS auth0_sub"))

    logger.info("Cleanup aplicado: user_id NOT NULL, user_email y auth0_sub eliminadas.")
    logger.warning(
        "IMPORTANTE: src/load/models.py todavía declara auth0_sub/user_email como columnas "
        "ORM — hay que quitarlas de AppUser/SavedAlert/CompetitorWatch (y de los schemas que "
        "las expongan) en el mismo commit que ejecuta este cleanup, o los SELECT de SQLAlchemy "
        "van a fallar contra columnas que ya no existen."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true", help="Solo verifica que es seguro aplicar el cleanup.")
    group.add_argument("--apply", action="store_true", help="Aplica el cleanup (destructivo, requiere backup).")
    args = parser.parse_args()
    run(apply=args.apply)
