"""Test de integración end-to-end (requiere contenedor db corriendo).

Ejecutar con:
    docker compose up -d db
    pytest tests/test_pipeline_e2e.py -v

Se salta automáticamente si DATABASE_URL no está en el entorno.
"""

import os
import pytest


DB_URL = os.getenv("DATABASE_URL")
pytestmark = pytest.mark.skipif(
    not DB_URL,
    reason="DATABASE_URL no disponible — se requiere el contenedor db para el test e2e.",
)


@pytest.fixture(scope="module")
def engine():
    from src.load.loader import create_tables, get_engine
    eng = get_engine(DB_URL)
    create_tables(eng)
    return eng


def test_pipeline_loads_valid_records(engine, sample_raw_records):
    from sqlalchemy.orm import Session
    from sqlalchemy import select, func
    from src.transform.normalize import normalize_record
    from src.transform.validate import validate_records
    from src.load.loader import load_batch
    from src.load.models import Contract

    normalized = [normalize_record(r) for r in sample_raw_records]
    result = validate_records(normalized)

    assert len(result.valid) > 0, "No hay registros válidos en el fixture."

    inserted, _ = load_batch(engine, result.valid, [], {}, {})
    assert inserted >= 0  # puede ser 0 si ya existían (idempotencia)

    # Verificar que las tablas tienen datos
    with Session(engine) as session:
        count = session.scalar(select(func.count()).select_from(Contract))
        assert count > 0


def test_pipeline_idempotent(engine, sample_raw_records):
    """Ejecutar el cargador dos veces no duplica registros."""
    from sqlalchemy.orm import Session
    from sqlalchemy import select, func
    from src.transform.normalize import normalize_record
    from src.transform.validate import validate_records
    from src.load.loader import load_batch
    from src.load.models import Contract

    normalized = [normalize_record(r) for r in sample_raw_records]
    result = validate_records(normalized)

    load_batch(engine, result.valid, [], {}, {})

    with Session(engine) as session:
        count_after_first = session.scalar(select(func.count()).select_from(Contract))

    load_batch(engine, result.valid, [], {}, {})

    with Session(engine) as session:
        count_after_second = session.scalar(select(func.count()).select_from(Contract))

    assert count_after_first == count_after_second, "La carga duplicó registros."


def test_rejected_records_persisted(engine, sample_raw_records):
    from sqlalchemy.orm import Session
    from sqlalchemy import select, func
    from src.transform.normalize import normalize_record
    from src.transform.validate import validate_records
    from src.load.loader import _persist_rejected
    from src.load.models import RejectedRecord

    normalized = [normalize_record(r) for r in sample_raw_records]
    result = validate_records(normalized)

    assert len(result.rejected) > 0, "No hay registros rechazados en el fixture."

    with Session(engine) as session:
        with session.begin():
            _persist_rejected(session, result.rejected)

    with Session(engine) as session:
        count = session.scalar(select(func.count()).select_from(RejectedRecord))
        assert count > 0
