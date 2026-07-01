"""Validación de registros antes de la carga.

Cada regla devuelve None si el registro es válido, o un string con el motivo
de rechazo. Esto permite agregar nuevas reglas sin tocar el bucle principal.
"""

import logging
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Callable

logger = logging.getLogger(__name__)

RuleFunc = Callable[[dict], str | None]


def _rule_valor_positivo(record: dict) -> str | None:
    raw = record.get("valor")
    if raw is None:
        return "valor_nulo"
    try:
        v = Decimal(str(raw))
    except InvalidOperation:
        return "valor_no_numerico"
    if v <= 0:
        return "valor_no_positivo"
    return None


def _rule_fecha_valida(record: dict) -> str | None:
    raw = record.get("fecha")
    if not raw:
        return "fecha_nula"
    if isinstance(raw, (datetime,)):
        return None
    # Intenta parsear formatos comunes de la API Socrata
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            datetime.strptime(str(raw)[:19], fmt[:len(fmt)])
            return None
        except ValueError:
            continue
    return "fecha_no_parseable"


def _rule_entidad_presente(record: dict) -> str | None:
    if not record.get("entidad_canonica"):
        return "entidad_vacia"
    return None


def _rule_proceso_de_compra_presente(record: dict) -> str | None:
    if not record.get("proceso_de_compra"):
        return "proceso_de_compra_vacio"
    return None


RULES: list[RuleFunc] = [
    _rule_valor_positivo,
    _rule_fecha_valida,
    _rule_entidad_presente,
    _rule_proceso_de_compra_presente,
]


class ValidationResult:
    __slots__ = ("valid", "rejected")

    def __init__(self) -> None:
        self.valid: list[dict] = []
        self.rejected: list[dict] = []


def validate_records(records: list[dict]) -> ValidationResult:
    """Clasifica cada registro en válido o rechazado."""
    result = ValidationResult()
    accepted = rejected = 0

    for record in records:
        motivo = None
        for rule in RULES:
            motivo = rule(record)
            if motivo:
                break

        if motivo:
            record["_motivo_rechazo"] = motivo
            result.rejected.append(record)
            rejected += 1
        else:
            result.valid.append(record)
            accepted += 1

    logger.info(
        "Validación: %d aceptados, %d rechazados (total=%d).",
        accepted, rejected, accepted + rejected,
    )
    return result
