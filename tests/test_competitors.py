"""Tests de src/api/routers/competitors.py (ver auth2.md FASE 7/9) —
propiedad y aislamiento por user.id.

follow_competitor() usa un upsert ON CONFLICT específico de Postgres
(sqlalchemy.dialects.postgresql.insert), que SQLite no soporta — esa parte
se verifica manualmente contra Neon real (ver docs/clerk-setup.md, sección
5) en vez de acá. Los tests de acá cubren list/unfollow, que sí son
portables, insertando las filas directo en la DB de test."""

import pytest

from src.api.deps import get_current_user
from src.api.main import app
from src.load.models import AppUser, CompetitorWatch, Subscription


def _make_pro_user(db_session, sub: str) -> AppUser:
    user = AppUser(auth_provider="clerk", auth_provider_user_id=sub, email=f"{sub}@example.com")
    db_session.add(user)
    db_session.commit()
    db_session.add(Subscription(user_id=user.id, plan="pro", status="active"))
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def as_user(db_session):
    def _set(user: AppUser):
        app.dependency_overrides[get_current_user] = lambda: user

    yield _set
    app.dependency_overrides.pop(get_current_user, None)


def test_list_competitors_scoped_to_owner(api_client, db_session, as_user):
    user_a = _make_pro_user(db_session, "user_comp_a")
    user_b = _make_pro_user(db_session, "user_comp_b")
    db_session.add_all([
        CompetitorWatch(user_id=user_a.id, supplier_name="Constructora A", is_active=True),
        CompetitorWatch(user_id=user_b.id, supplier_name="Constructora B", is_active=True),
    ])
    db_session.commit()

    as_user(user_a)
    listed = api_client.get("/api/competitors").json()

    assert len(listed) == 1
    assert listed[0]["supplier_name"] == "Constructora A"
    assert listed[0]["user_id"] == user_a.id


def test_cannot_unfollow_another_users_competitor(api_client, db_session, as_user):
    user_a = _make_pro_user(db_session, "user_comp_del_a")
    user_b = _make_pro_user(db_session, "user_comp_del_b")
    watch = CompetitorWatch(user_id=user_a.id, supplier_name="Constructora A", is_active=True)
    db_session.add(watch)
    db_session.commit()

    as_user(user_b)
    resp = api_client.delete(f"/api/competitors/{watch.id}")

    assert resp.status_code == 404
