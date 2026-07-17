"""Dependencias compartidas — engine SQLAlchemy, sesión de DB, identidad
Clerk y gating premium (ver auth2.md — migrado desde Auth0).

Principio de arquitectura: Clerk responde 'quién es el usuario'
(get_current_user/require_authenticated_user). ContrataData/Neon responde
'qué plan tiene y qué puede usar' (require_pro/require_feature) — nunca al
revés. El frontend nunca decide acceso premium de forma definitiva; estas
dependencias son la única fuente de verdad.
"""

import os
from datetime import datetime
from functools import lru_cache

from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker

from src.api.clerk import decode_clerk_token, fetch_clerk_user
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


def link_or_create_app_user(db: Session, sub: str, profile: dict, *, commit: bool = True) -> AppUser:
    """Busca/crea el AppUser por (auth_provider='clerk', auth_provider_user_id)
    — ver auth2.md FASE 6. auth0_sub ya NO se usa para resolver identidad
    (columna histórica, ver migrate_auth_clerk.py).

    Compartida entre get_current_user (login normal, 'profile' viene de la
    Backend API solo para usuarios nuevos) y clerk_webhooks.py (user.created/
    user.updated, 'profile' viene directo del payload del webhook — sin
    request adicional a Clerk). Si existe un AppUser previo (ej. migrado de
    Auth0) con ese mismo email VERIFICADO, lo vincula sin cambiar su id —
    así conserva su Subscription/PaymentReference. Nunca vincula por un
    email no verificado (regla obligatoria de auth2.md)."""
    user = db.execute(
        select(AppUser).where(AppUser.auth_provider == "clerk", AppUser.auth_provider_user_id == sub)
    ).scalar_one_or_none()

    if user is None:
        existing = None
        if profile["email"] and profile["email_verified"]:
            existing = db.execute(
                select(AppUser).where(func.lower(AppUser.email) == profile["email"].lower())
            ).scalar_one_or_none()

        if existing is not None:
            if existing.auth_provider == "clerk" and existing.auth_provider_user_id != sub:
                # No debería pasar (Clerk no permite dos cuentas con el mismo
                # email verificado), pero no se resuelve arbitrariamente si pasa.
                raise HTTPException(status_code=409, detail="Este email ya está vinculado a otra cuenta.")
            user = existing
            user.auth_provider = "clerk"
            user.auth_provider_user_id = sub
        else:
            user = AppUser(auth_provider="clerk", auth_provider_user_id=sub)
            db.add(user)

    user.is_active = True
    if profile["email"] and (user.email or "").lower() != profile["email"].lower():
        # app_users.email es UNIQUE — si otra cuenta ya tiene este email (caso
        # típico: email todavía sin verificar, así que no se vinculó arriba),
        # no se pisa esa fila ni se rompe la constraint; esta cuenta queda sin
        # email hasta que se resuelva (webhook user.updated posterior, o a mano).
        email_query = select(AppUser.id).where(func.lower(AppUser.email) == profile["email"].lower())
        if user.id is not None:
            email_query = email_query.where(AppUser.id != user.id)
        taken_by_other = db.execute(email_query).scalar_one_or_none()
        if taken_by_other is None:
            user.email = profile["email"]
    user.email_verified = profile["email_verified"] and user.email == profile["email"]
    if profile["name"]:
        user.name = profile["name"]
    if profile["picture"]:
        user.picture = profile["picture"]

    if commit:
        db.commit()
        db.refresh(user)
    return user


def _sync_app_user(db: Session, claims: dict) -> AppUser:
    """Camino de login: lookup rápido por auth_provider_user_id (sin red) si
    ya está vinculado; solo golpea la Backend API de Clerk (link_or_create_app_user)
    la primera vez que se ve este 'sub'. Nombre/foto se mantienen al día vía
    webhooks (user.updated), no en cada login."""
    sub = claims.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="Token sin 'sub'.")

    user = db.execute(
        select(AppUser).where(AppUser.auth_provider == "clerk", AppUser.auth_provider_user_id == sub)
    ).scalar_one_or_none()
    if user is None:
        profile = fetch_clerk_user(sub)
        user = link_or_create_app_user(db, sub, profile, commit=False)

    if not user.is_active:
        raise HTTPException(status_code=401, detail="Cuenta desactivada.")

    user.last_login_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> AppUser:
    """Valida el session token de Clerk del header 'Authorization: Bearer' y
    sincroniza (crea/vincula) el AppUser correspondiente en Neon."""
    if credentials is None:
        raise HTTPException(status_code=401, detail="Se requiere autenticación.")
    claims = decode_clerk_token(credentials.credentials)
    return _sync_app_user(db, claims)


# Alias explícito pedido en auth2.md — misma implementación que
# get_current_user, nombrado para dejar claro en los endpoints que la
# autenticación es obligatoria (backend neutral respecto al proveedor).
require_authenticated_user = get_current_user


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
