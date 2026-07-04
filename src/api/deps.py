"""Dependencias compartidas — engine SQLAlchemy, sesión de DB, identidad
Auth0 y gating premium (ver auth.md).

Principio de arquitectura: Auth0 responde 'quién es el usuario'
(get_current_user/require_auth0_user). ContrataData/Neon responde 'qué plan
tiene y qué puede usar' (require_pro/require_feature) — nunca al revés. El
frontend nunca decide acceso premium de forma definitiva; estas dependencias
son la única fuente de verdad.
"""

import os
from datetime import datetime
from functools import lru_cache

from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from src.api.auth0 import decode_auth0_token
from src.load.models import AppUser, PremiumEntitlement, Subscription

load_dotenv()

_bearer_scheme = HTTPBearer(auto_error=False)


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


class PremiumRequiredError(HTTPException):
    """403 con el shape exacto que espera el frontend para mostrar el
    paywall (ver auth.md) — no el {"detail": ...} por defecto de FastAPI,
    sino el objeto plano, vía el exception handler registrado en main.py."""

    def __init__(self) -> None:
        super().__init__(
            status_code=403,
            detail={
                "error": "premium_required",
                "plan_required": "pro",
                "message": "Esta función requiere ContrataData Pro.",
            },
        )


def _sync_app_user(db: Session, claims: dict) -> AppUser:
    sub = claims.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="Token sin 'sub'.")

    user = db.execute(select(AppUser).where(AppUser.auth0_sub == sub)).scalar_one_or_none()
    if user is None:
        user = AppUser(auth0_sub=sub)
        db.add(user)

    email = claims.get("email")
    if email:
        user.email = email
    user.email_verified = bool(claims.get("email_verified", False))
    if claims.get("name"):
        user.name = claims["name"]
    if claims.get("picture"):
        user.picture = claims["picture"]
    user.last_login_at = datetime.utcnow()

    db.commit()
    db.refresh(user)
    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> AppUser:
    """Valida el Access Token Auth0 del header 'Authorization: Bearer' y
    sincroniza (crea/actualiza) el AppUser correspondiente en Neon."""
    if credentials is None:
        raise HTTPException(status_code=401, detail="Se requiere autenticación.")
    claims = decode_auth0_token(credentials.credentials)
    return _sync_app_user(db, claims)


# Alias explícito pedido en auth.md — misma implementación que get_current_user,
# nombrado para dejar claro en los endpoints que la autenticación es obligatoria.
require_auth0_user = get_current_user


def get_latest_subscription(db: Session, user_id: int) -> Subscription | None:
    return db.execute(
        select(Subscription)
        .where(Subscription.user_id == user_id)
        .order_by(Subscription.updated_at.desc())
    ).scalars().first()


def _has_active_subscription(db: Session, user_id: int) -> bool:
    sub = get_latest_subscription(db, user_id)
    if sub is None or sub.plan != "pro" or sub.status not in ("active", "trialing"):
        return False
    if sub.current_period_end is not None and sub.current_period_end < datetime.utcnow():
        return False
    return True


def _has_entitlement(db: Session, user_id: int, feature_key: str) -> bool:
    ent = db.execute(
        select(PremiumEntitlement).where(
            PremiumEntitlement.user_id == user_id,
            PremiumEntitlement.feature_key == feature_key,
            PremiumEntitlement.is_enabled.is_(True),
        )
    ).scalars().first()
    if ent is None:
        return False
    if ent.expires_at is not None and ent.expires_at < datetime.utcnow():
        return False
    return True


def is_pro_user(db: Session, user: AppUser) -> bool:
    return _has_active_subscription(db, user.id)


def require_pro(
    user: AppUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AppUser:
    """Gating Pro general — cualquier plan pro activo desbloquea. Usar
    require_feature(key) en vez de esta si la feature admite entitlements
    puntuales (créditos beta) para usuarios Free."""
    if not _has_active_subscription(db, user.id):
        raise PremiumRequiredError()
    return user


def require_feature(feature_key: str):
    """Factory: gating por feature específica — plan pro activo, O un
    PremiumEntitlement puntual para 'feature_key' (créditos beta, cortesías
    manuales) sin necesidad de ser pro en general."""

    def _dependency(
        user: AppUser = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> AppUser:
        if _has_active_subscription(db, user.id) or _has_entitlement(db, user.id, feature_key):
            return user
        raise PremiumRequiredError()

    return _dependency
