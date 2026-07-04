"""Utilidad de admin: marcar un usuario como Pro (o revertirlo) creando/
actualizando su Subscription (ver auth.md). Reemplaza al admin_set_premium.py
anterior (que operaba sobre la tabla premium_users del modelo email-based,
ver scalability.md — ya sin uso tras la migración a Auth0).

Requiere que el usuario ya exista en app_users, es decir que haya iniciado
sesión al menos una vez (GET /api/me sincroniza el AppUser en su primer
login) — no hay backoffice todavía, así que esto aplica manualmente el
resultado de un pago coordinado fuera de banda.

Uso:
    python admin_set_pro.py usuario@ejemplo.com --status active
    python admin_set_pro.py usuario@ejemplo.com --status active --until 2026-12-31
    python admin_set_pro.py usuario@ejemplo.com --plan free --status expired
"""

import argparse
import logging
import os
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.load.loader import get_engine
from src.load.models import AppUser, Subscription

load_dotenv()
logging.basicConfig(level="INFO", format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("admin_set_pro")


def run(email: str, plan: str, status: str, until: str | None) -> None:
    email = email.strip().lower()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise EnvironmentError("DATABASE_URL no está configurada.")

    engine = get_engine(database_url)
    current_period_end = datetime.strptime(until, "%Y-%m-%d") if until else None
    now = datetime.utcnow()

    with Session(engine) as session:
        with session.begin():
            user = session.execute(select(AppUser).where(AppUser.email == email)).scalar_one_or_none()
            if user is None:
                raise RuntimeError(
                    f"No existe un app_user con email='{email}'. El usuario debe iniciar "
                    "sesión al menos una vez (Auth0 → GET /api/me lo sincroniza) antes de "
                    "poder marcarlo como Pro."
                )

            sub = session.execute(
                select(Subscription)
                .where(Subscription.user_id == user.id)
                .order_by(Subscription.updated_at.desc())
            ).scalars().first()

            if sub is None:
                sub = Subscription(user_id=user.id, provider="manual")
                session.add(sub)

            sub.plan = plan
            sub.status = status
            sub.provider = sub.provider or "manual"
            sub.current_period_end = current_period_end
            sub.updated_at = now

        user_id = user.id

    logger.info(
        "%s (user_id=%d) → plan=%s, status=%s, current_period_end=%s",
        email, user_id, plan, status,
        current_period_end.date() if current_period_end else None,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("email")
    parser.add_argument("--plan", choices=["free", "pro"], default="pro")
    parser.add_argument(
        "--status",
        choices=["trialing", "active", "past_due", "canceled", "expired"],
        default="active",
    )
    parser.add_argument("--until", metavar="YYYY-MM-DD", default=None)
    args = parser.parse_args()
    run(args.email, args.plan, args.status, args.until)
