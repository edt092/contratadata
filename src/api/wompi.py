"""Integración con Wompi (ver auth.md y API-WOMPI-CONTRATADATA.txt): firma
de integridad para el widget de checkout y verificación de checksum de los
eventos/webhook. Algoritmos tomados de docs.wompi.co — ambos son SHA-256 hex
de una concatenación de campos + un secreto, nunca expuestos al frontend."""

import hashlib
import os


def build_integrity_signature(reference: str, amount_in_cents: int, currency: str = "COP") -> str:
    """Firma que el widget de checkout necesita en 'data-signature:integrity'.
    Debe generarse server-side: expone el WOMPI_INTEGRITY_SECRET a quien la
    calcule, así que nunca se hace en el navegador."""
    secret = os.environ["WOMPI_INTEGRITY_SECRET"]
    raw = f"{reference}{amount_in_cents}{currency}{secret}"
    return hashlib.sha256(raw.encode()).hexdigest()


def _resolve_path(data: dict, path: str):
    node = data
    for part in path.split("."):
        node = node[part]
    return node


def verify_event_checksum(payload: dict) -> bool:
    """Valida la autenticidad de un evento entrante (POST /webhooks/wompi):
    concatena los valores de signature.properties (en orden) + timestamp +
    WOMPI_EVENTS_SECRET, SHA-256 hex, y compara contra signature.checksum."""
    secret = os.environ["WOMPI_EVENTS_SECRET"]
    props = payload["signature"]["properties"]
    concatenated = "".join(str(_resolve_path(payload["data"], p)) for p in props)
    raw = f"{concatenated}{payload['timestamp']}{secret}"
    expected = hashlib.sha256(raw.encode()).hexdigest()
    return expected == payload["signature"]["checksum"]
