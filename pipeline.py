"""Punto de entrada del pipeline ETL de ContrataData.

Ejecuta las etapas en orden: extract → normalize → validate → load.
Procesa en lotes de BATCH_SIZE registros con un commit por lote,
de modo que una caída parcial no pierde el progreso ya guardado.
"""

import logging
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from itertools import islice

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("pipeline")

BATCH_SIZE = 5_000


def _iter_chunks(iterable, size: int):
    it = iter(iterable)
    while chunk := list(islice(it, size)):
        yield chunk


def _write_github_summary(
    *,
    modo: str,
    total_extraidos: int,
    total_insertados: int,
    total_duplicados: int,
    total_rechazados: int,
    lotes_fallidos: int,
    lote_num: int,
    motivos_global: Counter,
) -> None:
    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return
    estado = "✅ OK" if lotes_fallidos == 0 else f"⚠️ {lotes_fallidos}/{lote_num} lotes fallidos"
    lines = [
        "## ContrataData ETL — Resumen\n\n",
        f"| Campo | Valor |\n|---|---|\n",
        f"| Modo | `{modo}` |\n",
        f"| Estado carga | {estado} |\n",
        f"| Registros extraídos | {total_extraidos:,} |\n",
        f"| Insertados | {total_insertados:,} |\n",
        f"| Duplicados (skip) | {total_duplicados:,} |\n",
        f"| Rechazados | {total_rechazados:,} |\n",
    ]
    if motivos_global:
        lines.append("\n### Motivos de rechazo\n\n")
        for motivo, n in motivos_global.most_common(10):
            lines.append(f"- `{motivo}`: {n:,}\n")
    try:
        with open(summary_path, "a", encoding="utf-8") as fh:
            fh.writelines(lines)
    except OSError as exc:
        logger.warning("No se pudo escribir GITHUB_STEP_SUMMARY: %s", exc)


def run() -> None:
    from src.error_log import PipelineErrorLog
    from src.extract.secop_socrata import SecopSocrataExtractor
    from src.transform.normalize import normalize_record
    from src.transform.validate import validate_records
    from src.load.loader import get_engine, create_tables, load_batch, get_last_run_at, set_last_run_at

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise EnvironmentError("DATABASE_URL no está configurada.")

    run_started_at = datetime.now(timezone.utc).replace(tzinfo=None)

    engine = get_engine(database_url)
    create_tables(engine)

    # Determinar modo: incremental (last_run_at en DB) o completo
    last_run_at = get_last_run_at(engine)
    force_full = os.getenv("FORCE_FULL_LOAD", "").lower() in ("1", "true", "yes")

    if force_full or last_run_at is None:
        since = None
        modo = "COMPLETO" if last_run_at is None else "COMPLETO (forzado)"
    else:
        since = last_run_at
        modo = f"INCREMENTAL desde {last_run_at.isoformat()}"

    logger.info("=== Iniciando pipeline ContrataData — modo %s (lotes de %d) ===", modo, BATCH_SIZE)

    with PipelineErrorLog() as err:
        extractor = SecopSocrataExtractor(
            max_records=int(os.getenv("MAX_RECORDS", "0")) or None,
            date_from=os.getenv("DATE_FROM"),
            since=since,
            error_log=err,
        )

        # Cachés de entidades y proveedores compartidos entre lotes
        # para evitar SELECTs repetidos a la BD
        entity_cache: dict = {}
        supplier_cache: dict = {}

        total_extraidos = total_insertados = total_duplicados = total_rechazados = 0
        motivos_global: Counter = Counter()
        lote_num = 0
        lotes_fallidos = 0

        for chunk in _iter_chunks(extractor.extract(), BATCH_SIZE):
            lote_num += 1
            total_extraidos += len(chunk)

            # Normalizar y validar el lote
            normalized = [normalize_record(r) for r in chunk]
            result = validate_records(normalized)

            # Contabilizar rechazos
            for rec in result.rejected:
                motivos_global[rec.get("_motivo_rechazo", "desconocido")] += 1
            total_rechazados += len(result.rejected)

            # Cargar lote con su propio commit
            try:
                inserted, skipped = load_batch(
                    engine, result.valid, result.rejected,
                    entity_cache, supplier_cache,
                )
            except Exception as exc:
                lotes_fallidos += 1
                msg = f"Lote {lote_num} (offset ~{total_extraidos}): {type(exc).__name__}: {exc}"
                err.log("Carga — Error de lote", msg)
                logger.error("Error en lote %d, continuando con el siguiente. %s", lote_num, exc)
                continue

            total_insertados += inserted
            total_duplicados += skipped

            if lote_num % 10 == 0:
                logger.info(
                    "Progreso — lote %d | extraídos: %d | insertados: %d | rechazados: %d",
                    lote_num, total_extraidos, total_insertados, total_rechazados,
                )

        # Resumen final
        logger.info(
            "=== Pipeline finalizado === extraídos: %d | insertados: %d | "
            "duplicados: %d | rechazados: %d | lotes_fallidos: %d",
            total_extraidos, total_insertados, total_duplicados, total_rechazados, lotes_fallidos,
        )

        if motivos_global:
            resumen = ", ".join(f"{m}: {n}" for m, n in motivos_global.most_common())
            err.log(
                "Validación — Rechazos totales",
                f"{total_rechazados} registros rechazados — {resumen}",
            )

        # Escribir Job Summary para GitHub Actions (visible directo en la UI)
        _write_github_summary(
            modo=modo,
            total_extraidos=total_extraidos,
            total_insertados=total_insertados,
            total_duplicados=total_duplicados,
            total_rechazados=total_rechazados,
            lotes_fallidos=lotes_fallidos,
            lote_num=lote_num,
            motivos_global=motivos_global,
        )

        # Falla explícita si todos los lotes con datos fallaron al cargar
        if lote_num > 0 and lotes_fallidos == lote_num:
            raise RuntimeError(
                f"Todos los lotes fallaron al cargar ({lotes_fallidos}/{lote_num}). "
                "Revisa la conexión a la base de datos y los logs anteriores."
            )

        # Marcar corrida exitosa para la próxima ejecución incremental
        set_last_run_at(engine, run_started_at)
        logger.info("Timestamp de corrida guardado: %s", run_started_at.isoformat())


if __name__ == "__main__":
    try:
        run()
    except Exception as exc:
        logger.critical("Pipeline terminó con error fatal: %s: %s", type(exc).__name__, exc)
        summary_path = os.getenv("GITHUB_STEP_SUMMARY")
        if summary_path:
            try:
                with open(summary_path, "a", encoding="utf-8") as fh:
                    fh.write(f"\n## ❌ Error fatal\n\n```\n{type(exc).__name__}: {exc}\n```\n")
            except OSError:
                pass
        sys.exit(1)
