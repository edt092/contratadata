"""Tests de src/api/routers/alerts.py (ver auth2.md FASE 7/9) — propiedad y
aislamiento por user.id, no por email/query param espoofeable."""

import pytest

from src.api.deps import get_current_user
from src.api.main import app
from src.load.models import AppUser, Subscription


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
    """Override de get_current_user para simular una sesión ya autenticada
    — la validación del token en sí ya la cubre tests/test_clerk.py."""
    def _set(user: AppUser):
        app.dependency_overrides[get_current_user] = lambda: user

    yield _set
    app.dependency_overrides.pop(get_current_user, None)


def test_create_and_list_alert_scoped_to_owner(api_client, db_session, as_user):
    user_a = _make_pro_user(db_session, "user_alerts_a")
    as_user(user_a)

    resp = api_client.post("/api/alerts", json={"name": "Mi alerta", "frecuencia": "daily"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["user_id"] == user_a.id

    listed = api_client.get("/api/alerts").json()
    assert len(listed) == 1
    assert listed[0]["user_id"] == user_a.id


def test_alerts_isolated_between_users(api_client, db_session, as_user):
    user_a = _make_pro_user(db_session, "user_alerts_iso_a")
    user_b = _make_pro_user(db_session, "user_alerts_iso_b")

    as_user(user_a)
    api_client.post("/api/alerts", json={"name": "Alerta de A", "frecuencia": "daily"})

    as_user(user_b)
    resp = api_client.get("/api/alerts")
    assert resp.json() == []


def test_cannot_update_or_delete_another_users_alert(api_client, db_session, as_user):
    user_a = _make_pro_user(db_session, "user_alerts_del_a")
    user_b = _make_pro_user(db_session, "user_alerts_del_b")

    as_user(user_a)
    alert_id = api_client.post("/api/alerts", json={"name": "Alerta de A", "frecuencia": "daily"}).json()["id"]

    as_user(user_b)
    patch_resp = api_client.patch(f"/api/alerts/{alert_id}", json={"is_active": False})
    delete_resp = api_client.delete(f"/api/alerts/{alert_id}")

    assert patch_resp.status_code == 404
    assert delete_resp.status_code == 404
