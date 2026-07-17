"""Tests de src/api/deps.py::link_or_create_app_user (ver auth2.md FASE 6/9)
— vinculación/creación de AppUser por identidad de Clerk, sin decodificar
JWTs reales (eso lo cubre tests/test_clerk.py) ni golpear la Backend API de
Clerk (eso lo cubre tests/test_webhooks_clerk.py, donde el payload ya viene
completo del webhook)."""

import pytest
from fastapi import HTTPException
from sqlalchemy import select

from src.api.deps import link_or_create_app_user
from src.load.models import AppUser

VERIFIED_PROFILE = {
    "email": "usuario@example.com",
    "email_verified": True,
    "name": "Usuario Prueba",
    "picture": "https://img.clerk.com/pic.png",
}

UNVERIFIED_PROFILE = {
    "email": "sinverificar@example.com",
    "email_verified": False,
    "name": None,
    "picture": None,
}


def test_creates_new_app_user_when_no_match(db_session):
    user = link_or_create_app_user(db_session, "user_clerk_1", VERIFIED_PROFILE)

    assert user.id is not None
    assert user.auth_provider == "clerk"
    assert user.auth_provider_user_id == "user_clerk_1"
    assert user.email == "usuario@example.com"
    assert user.email_verified is True
    assert user.is_active is True


def test_returns_same_user_on_second_call_same_sub(db_session):
    first = link_or_create_app_user(db_session, "user_clerk_1", VERIFIED_PROFILE)
    second = link_or_create_app_user(db_session, "user_clerk_1", VERIFIED_PROFILE)

    assert first.id == second.id
    count = db_session.execute(select(AppUser)).scalars().all()
    assert len(count) == 1


def test_links_to_existing_legacy_user_by_verified_email_without_changing_id(db_session):
    # Usuario migrado de Auth0 (ver migrate_auth_clerk.py): ya tiene un id,
    # auth_provider='auth0', mismo email verificado.
    legacy = AppUser(
        auth0_sub="auth0|legacy123",
        auth_provider="auth0",
        auth_provider_user_id="auth0|legacy123",
        email="usuario@example.com",
        email_verified=True,
    )
    db_session.add(legacy)
    db_session.commit()
    legacy_id = legacy.id

    linked = link_or_create_app_user(db_session, "user_clerk_new", VERIFIED_PROFILE)

    assert linked.id == legacy_id  # conserva el id -> Subscription/PaymentReference intactos
    assert linked.auth_provider == "clerk"
    assert linked.auth_provider_user_id == "user_clerk_new"


def test_unverified_email_does_not_link_existing_account(db_session):
    legacy = AppUser(
        auth0_sub="auth0|legacy456",
        auth_provider="auth0",
        auth_provider_user_id="auth0|legacy456",
        email="sinverificar@example.com",
        email_verified=True,
    )
    db_session.add(legacy)
    db_session.commit()
    legacy_id = legacy.id

    # El profile nuevo tiene el MISMO email pero SIN verificar -> no vincula,
    # crea una cuenta nueva separada (regla obligatoria de auth2.md).
    created = link_or_create_app_user(db_session, "user_clerk_new", UNVERIFIED_PROFILE)

    assert created.id != legacy_id
    assert created.auth_provider_user_id == "user_clerk_new"


def test_email_collision_raises_409(db_session):
    # Ya hay un AppUser vinculado a OTRO sub de Clerk con este mismo email
    # verificado -> no se resuelve arbitrariamente.
    other = AppUser(
        auth_provider="clerk",
        auth_provider_user_id="user_clerk_other",
        email="usuario@example.com",
        email_verified=True,
    )
    db_session.add(other)
    db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        link_or_create_app_user(db_session, "user_clerk_new", VERIFIED_PROFILE)
    assert exc_info.value.status_code == 409


def test_reactivates_user_on_new_profile_sync(db_session):
    user = link_or_create_app_user(db_session, "user_clerk_1", VERIFIED_PROFILE)
    user.is_active = False
    db_session.commit()

    resynced = link_or_create_app_user(db_session, "user_clerk_1", VERIFIED_PROFILE)
    assert resynced.is_active is True
