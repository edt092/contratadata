"""Punto de entrada del pipeline ETL de ContrataData.

Ejecuta las etapas en orden: extract → normalize → validate → load.
"""

import logging
import os

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("pipeline")


def run() -> None:
    from src.extract.secop_socrata import SecopSocrataExtractor
    from src.transform.normalize import normalize_record
    from src.transform.validate import validate_records
    from src.load.loader import run_load

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise EnvironmentError("DATABASE_URL no está configurada.")

    logger.info("=== Iniciando pipeline ContrataData ===")

    # ── Extracción ────────────────────────────────────────────────────────
    extractor = SecopSocrataExtractor(
        max_records=int(os.getenv("MAX_RECORDS", "0")) or None,
    )
    raw_records = list(extractor.extract())
    logger.info("Registros extraídos: %d", len(raw_records))

    # ── Normalización ─────────────────────────────────────────────────────
    normalized = [normalize_record(r) for r in raw_records]

    # ── Validación ────────────────────────────────────────────────────────
    result = validate_records(normalized)

    # ── Carga ─────────────────────────────────────────────────────────────
    run_load(database_url, result.valid, result.rejected)

    logger.info("=== Pipeline finalizado ===")


if __name__ == "__main__":
    run()
