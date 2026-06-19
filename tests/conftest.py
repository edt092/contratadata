"""Fixtures compartidos por todos los tests."""

import json
import pathlib

import pytest


@pytest.fixture()
def sample_raw_records():
    fixture_path = pathlib.Path(__file__).parent / "fixtures" / "sample_secop_response.json"
    raw = json.loads(fixture_path.read_text(encoding="utf-8"))
    # Mapear al formato interno igual que hace SecopSocrataExtractor._normalize_raw
    from src.extract.secop_socrata import SecopSocrataExtractor
    return [SecopSocrataExtractor._normalize_raw(r) for r in raw]
