"""Normalización de nombres de entidades a su forma canónica.

El diccionario ENTITY_MAP es la única fuente de verdad para la normalización.
Está definido como dato (no lógica) para que sea versionable y extensible
sin tocar el código de la capa de transformación.
"""

import logging
import re

logger = logging.getLogger(__name__)

# Diccionario: clave = variante (lowercase, sin tildes ni puntuación extra)
#              valor = nombre canónico oficial
ENTITY_MAP: dict[str, str] = {
    # ── Ministerio TIC ─────────────────────────────────────────────────────
    "ministerio tic": "Ministerio de Tecnologías de la Información y las Comunicaciones",
    "min tic": "Ministerio de Tecnologías de la Información y las Comunicaciones",
    "mintic": "Ministerio de Tecnologías de la Información y las Comunicaciones",
    "ministerio de tecnologias de la informacion y las comunicaciones":
        "Ministerio de Tecnologías de la Información y las Comunicaciones",
    # ── Ministerio de Salud ────────────────────────────────────────────────
    "minsalud": "Ministerio de Salud y Protección Social",
    "min salud": "Ministerio de Salud y Protección Social",
    "ministerio de salud": "Ministerio de Salud y Protección Social",
    "ministerio de salud y proteccion social":
        "Ministerio de Salud y Protección Social",
    # ── Ministerio de Educación ────────────────────────────────────────────
    "mineducacion": "Ministerio de Educación Nacional",
    "min educacion": "Ministerio de Educación Nacional",
    "ministerio de educacion": "Ministerio de Educación Nacional",
    "ministerio de educacion nacional": "Ministerio de Educación Nacional",
    # ── Ministerio de Hacienda ─────────────────────────────────────────────
    "minhacienda": "Ministerio de Hacienda y Crédito Público",
    "min hacienda": "Ministerio de Hacienda y Crédito Público",
    "ministerio de hacienda": "Ministerio de Hacienda y Crédito Público",
    # ── DNP ───────────────────────────────────────────────────────────────
    "dnp": "Departamento Nacional de Planeación",
    "departamento nacional de planeacion": "Departamento Nacional de Planeación",
    # ── INVIAS ────────────────────────────────────────────────────────────
    "invias": "Instituto Nacional de Vías",
    "instituto nacional de vias": "Instituto Nacional de Vías",
    # ── SENA ──────────────────────────────────────────────────────────────
    "sena": "Servicio Nacional de Aprendizaje",
    "servicio nacional de aprendizaje": "Servicio Nacional de Aprendizaje",
    # ── ICBF ──────────────────────────────────────────────────────────────
    "icbf": "Instituto Colombiano de Bienestar Familiar",
    "instituto colombiano de bienestar familiar":
        "Instituto Colombiano de Bienestar Familiar",
    # ── Colombia Compra Eficiente ──────────────────────────────────────────
    "colombia compra eficiente": "Colombia Compra Eficiente",
    "agencia nacional de contratacion publica":
        "Colombia Compra Eficiente",
}


def _clean_key(name: str) -> str:
    """Convierte a minúsculas, elimina tildes y colapsa espacios múltiples."""
    replacements = str.maketrans("áéíóúüñÁÉÍÓÚÜÑ", "aeiouunAEIOUUN")
    cleaned = name.translate(replacements).lower()
    cleaned = re.sub(r"[^\w\s]", " ", cleaned)  # signos de puntuación → espacio
    return re.sub(r"\s+", " ", cleaned).strip()


def resolve_entity(raw_name: str) -> str | None:
    """Devuelve el nombre canónico o None si no puede resolverse."""
    if not raw_name or not raw_name.strip():
        return None
    key = _clean_key(raw_name)
    canonical = ENTITY_MAP.get(key)
    if canonical:
        return canonical
    # Búsqueda parcial: si la clave del mapa está contenida en el nombre limpio
    for map_key, canonical_name in ENTITY_MAP.items():
        if map_key in key or key in map_key:
            logger.debug("Coincidencia parcial: '%s' → '%s'", raw_name, canonical_name)
            return canonical_name
    logger.debug("Entidad no resoluble: '%s'", raw_name)
    return None


def normalize_record(record: dict) -> dict:
    """Agrega 'entidad_canonica' al registro; no modifica el original."""
    result = dict(record)
    raw_name = record.get("entidad", "")
    result["entidad_canonica"] = resolve_entity(raw_name) or raw_name.strip() or None
    return result
