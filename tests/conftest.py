"""Fixtures compartidos por todos los tests."""

import json
import pathlib

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture()
def sample_raw_records():
    fixture_path = pathlib.Path(__file__).parent / "fixtures" / "sample_secop_response.json"
    raw = json.loads(fixture_path.read_text(encoding="utf-8"))
    # Mapear al formato interno igual que hace SecopSocrataExtractor._normalize_raw
    from src.extract.secop_socrata import SecopSocrataExtractor
    return [SecopSocrataExtractor._normalize_raw(r) for r in raw]


# ── DB de tests (ver auth2.md FASE 9) ────────────────────────────────────────
# SQLite en memoria: rápido, sin infra de CI adicional. Válido para AppUser/
# SavedAlert/CompetitorWatch/Subscription/PremiumEntitlement/PaymentReference
# (ninguno usa JSONB ni features Postgres-only) — NO válido para el upsert
# ON CONFLICT de competitors.py::follow_competitor (Postgres-specific), que
# queda fuera de esta suite y se verifica manualmente (ver docs/clerk-setup.md).

_AUTH_TABLES = [
    "app_users", "subscriptions", "premium_entitlements", "premium_leads",
    "saved_alerts", "competitor_watchlist", "payment_references",
]


@pytest.fixture()
def db_session():
    from src.load.models import Base

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine, tables=[Base.metadata.tables[t] for t in _AUTH_TABLES])
    factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    session: Session = factory()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture()
def api_client(db_session):
    """TestClient de la app FastAPI real, con get_db y la identidad
    (require_authenticated_user) inyectables por test — no decodifica JWTs
    reales acá, eso ya lo cubre tests/test_clerk.py."""
    from fastapi.testclient import TestClient

    from src.api.deps import get_db
    from src.api.main import app

    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_db, None)
