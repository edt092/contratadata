"""Tests del adaptador SecopSocrataExtractor (sin red — usa fixture JSON)."""

import json
import pathlib

import pytest
import responses as rsps_lib

from src.extract.secop_socrata import ENDPOINT, SecopSocrataExtractor


FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "sample_secop_response.json"


@rsps_lib.activate
def test_extract_yields_correct_fields():
    """El extractor mapea los campos Socrata a la interfaz interna."""
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    rsps_lib.add(rsps_lib.GET, ENDPOINT, json=payload, status=200)
    # Segunda llamada devuelve página vacía → termina la paginación
    rsps_lib.add(rsps_lib.GET, ENDPOINT, json=[], status=200)

    extractor = SecopSocrataExtractor()
    records = list(extractor.extract())

    assert len(records) == len(payload)
    required_fields = {"entidad", "contratista", "valor", "fecha", "estado", "fuente"}
    for rec in records:
        assert required_fields.issubset(rec.keys()), f"Faltan campos en: {rec}"


@rsps_lib.activate
def test_extract_fuente_es_secop_socrata():
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    rsps_lib.add(rsps_lib.GET, ENDPOINT, json=payload, status=200)
    rsps_lib.add(rsps_lib.GET, ENDPOINT, json=[], status=200)

    records = list(SecopSocrataExtractor().extract())
    assert all(r["fuente"] == "SECOP_SOCRATA" for r in records)


@rsps_lib.activate
def test_extract_respects_max_records():
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    rsps_lib.add(rsps_lib.GET, ENDPOINT, json=payload, status=200)

    records = list(SecopSocrataExtractor(max_records=2).extract())
    assert len(records) == 2


@rsps_lib.activate
def test_extract_handles_http_error(caplog):
    rsps_lib.add(rsps_lib.GET, ENDPOINT, status=503)
    rsps_lib.add(rsps_lib.GET, ENDPOINT, status=503)
    rsps_lib.add(rsps_lib.GET, ENDPOINT, status=503)

    records = list(SecopSocrataExtractor().extract())
    assert records == []
