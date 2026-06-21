"""Tests de normalización y validación."""

import pytest

from src.transform.normalize import normalize_record, resolve_entity
from src.transform.validate import validate_records


# ── Normalización ────────────────────────────────────────────────────────────

@pytest.mark.parametrize("variant", [
    "MINISTERIO TIC", "MIN TIC", "MinTIC", "mintic",
    "Ministerio de Tecnologias de la Informacion y las Comunicaciones",
])
def test_resolve_entity_mintic_variants(variant):
    canonical = resolve_entity(variant)
    assert canonical == "Ministerio de Tecnologías de la Información y las Comunicaciones"


def test_resolve_entity_unknown_returns_none():
    assert resolve_entity("ENTIDAD FANTASMA XYZ 9999") is None


def test_resolve_entity_empty_returns_none():
    assert resolve_entity("") is None
    assert resolve_entity("   ") is None


def test_normalize_record_adds_canonical(sample_raw_records):
    for rec in sample_raw_records:
        result = normalize_record(rec)
        assert "entidad_canonica" in result


# ── Validación ───────────────────────────────────────────────────────────────

def _make_valid_record(**overrides) -> dict:
    base = {
        "entidad": "SENA",
        "entidad_canonica": "Servicio Nacional de Aprendizaje",
        "contratista": "PROVEEDOR S.A.",
        "valor": "5000000",
        "fecha": "2024-01-15T00:00:00.000",
        "estado": "En ejecución",
        "fuente": "SECOP_SOCRATA",
        "_raw": {},
    }
    base.update(overrides)
    return base


def test_valid_record_passes():
    result = validate_records([_make_valid_record()])
    assert len(result.valid) == 1
    assert len(result.rejected) == 0


def test_valor_cero_es_rechazado():
    rec = _make_valid_record(valor="0")
    result = validate_records([rec])
    assert len(result.rejected) == 1
    assert result.rejected[0]["_motivo_rechazo"] == "valor_no_positivo"


def test_valor_negativo_es_rechazado():
    rec = _make_valid_record(valor="-500")
    result = validate_records([rec])
    assert result.rejected[0]["_motivo_rechazo"] == "valor_no_positivo"


def test_valor_nulo_es_rechazado():
    rec = _make_valid_record(valor=None)
    result = validate_records([rec])
    assert result.rejected[0]["_motivo_rechazo"] == "valor_nulo"


def test_fecha_nula_es_rechazada():
    rec = _make_valid_record(fecha=None)
    result = validate_records([rec])
    assert result.rejected[0]["_motivo_rechazo"] == "fecha_nula"


def test_entidad_no_resoluble_es_rechazada():
    rec = _make_valid_record(entidad_canonica=None)
    result = validate_records([rec])
    assert result.rejected[0]["_motivo_rechazo"] == "entidad_vacia"


def test_mixed_batch(sample_raw_records):
    """El fixture tiene 2 válidos y 2 rechazados."""
    from src.transform.normalize import normalize_record
    normalized = [normalize_record(r) for r in sample_raw_records]
    result = validate_records(normalized)
    # Registro 3 (valor negativo) y 4 (fecha nula / entidad desconocida) deben rechazarse
    assert len(result.valid) + len(result.rejected) == len(sample_raw_records)
    assert len(result.rejected) >= 2
