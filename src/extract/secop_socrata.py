"""Adaptador de extracción: SECOP II via API SODA (datos.gov.co).

Dataset: "SECOP II - Contratos Electrónicos"
Endpoint: https://www.datos.gov.co/resource/jbjy-vk9h.json

Documentación SODA: https://dev.socrata.com/consumers/getting-started.html
"""

import logging
import os
import random
import time
from datetime import datetime
from typing import TYPE_CHECKING, Iterator

import requests

from src.extract.base import BaseExtractor

if TYPE_CHECKING:
    from src.error_log import PipelineErrorLog

logger = logging.getLogger(__name__)

ENDPOINT = "https://www.datos.gov.co/resource/jbjy-vk9h.json"
PAGE_SIZE = 1000
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "7"))
BACKOFF_SECONDS = float(os.getenv("BACKOFF_SECONDS", "5"))
MAX_BACKOFF_SECONDS = float(os.getenv("MAX_BACKOFF_SECONDS", "120"))
REQUEST_TIMEOUT = 60
PAGE_DELAY = float(os.getenv("PAGE_DELAY", "0.3"))  # configurable vía env


class SecopExtractionError(RuntimeError):
    """Se agotaron los reintentos contra la API de Socrata.

    Se lanza en vez de devolver una página vacía para que un caído total
    del feed no se confunda con "no hay más páginas" y el pipeline falle
    de forma explícita en lugar de terminar silenciosamente con pocos
    registros.
    """


class SecopSocrataExtractor(BaseExtractor):
    SOURCE_NAME = "SECOP_SOCRATA"

    def __init__(
        self,
        app_token: str | None = None,
        max_records: int | None = None,
        date_from: str | None = None,
        since: datetime | None = None,
        error_log: "PipelineErrorLog | None" = None,
    ):
        self._app_token = app_token or os.getenv("SOCRATA_APP_TOKEN")
        self._max_records = max_records
        self._date_from = date_from or os.getenv("DATE_FROM")
        self._since = since  # filtro incremental por :updated_at
        self._error_log = error_log

    def _build_headers(self) -> dict:
        headers = {"Accept": "application/json"}
        if self._app_token:
            headers["X-App-Token"] = self._app_token
        return headers

    @staticmethod
    def _compute_backoff(attempt: int, retry_after: str | None) -> float:
        """Backoff exponencial con jitter; respeta Retry-After si el servidor lo envía."""
        if retry_after:
            try:
                return float(retry_after)
            except ValueError:
                pass
        base = min(BACKOFF_SECONDS * (2 ** (attempt - 1)), MAX_BACKOFF_SECONDS)
        return base + random.uniform(0, base * 0.25)

    def _build_where(self, last_id: str | None) -> str | None:
        conditions = []
        if self._since:
            # Incremental: solo registros añadidos/modificados en Socrata desde la última corrida
            conditions.append(f":updated_at >= '{self._since.strftime('%Y-%m-%dT%H:%M:%S')}'")
        if self._date_from:
            # Filtro manual por fecha de firma (backfill o carga inicial acotada)
            conditions.append(f"fecha_de_firma >= '{self._date_from}'")
        if last_id is not None:
            # Paginación por cursor estable en vez de $offset: en Socrata (Socrata SODA2)
            # los offsets profundos se degradan y son frágiles. ':id' es único y estable
            # bajo el mismo $order, así que ':id < último visto' avanza sin re-escanear.
            conditions.append(f":id < '{last_id}'")
        return " AND ".join(conditions) if conditions else None

    def _fetch_page(self, last_id: str | None) -> list[dict]:
        last_exc: Exception | None = None
        params = {
            "$limit": PAGE_SIZE,
            "$select": (
                ":id,"
                ":updated_at,"
                "nombre_entidad,"
                "proveedor_adjudicado,"
                "valor_del_contrato,"
                "fecha_de_firma,"
                "estado_contrato,"
                "proceso_de_compra,"
                "documento_proveedor,"
                "nit_entidad"
            ),
            "$order": ":id DESC",
        }
        where = self._build_where(last_id)
        if where:
            params["$where"] = where

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                resp = requests.get(
                    ENDPOINT,
                    headers=self._build_headers(),
                    params=params,
                    timeout=REQUEST_TIMEOUT,
                )
                resp.raise_for_status()
                return resp.json()
            except requests.RequestException as exc:
                last_exc = exc
                logger.warning(
                    "Intento %d/%d fallido (last_id=%s, where=%s): %s",
                    attempt, MAX_RETRIES, last_id, where, exc,
                )
                if attempt < MAX_RETRIES:
                    retry_after = None
                    if exc.response is not None:
                        retry_after = exc.response.headers.get("Retry-After")
                    time.sleep(self._compute_backoff(attempt, retry_after))
        msg = f"Se agotaron los reintentos en last_id={last_id} (where={where}): {last_exc}"
        logger.error(msg)
        if self._error_log:
            self._error_log.log("Extracción — API", msg)
        raise SecopExtractionError(msg) from last_exc

    def extract(self) -> Iterator[dict]:
        last_id: str | None = None
        total_yielded = 0

        logger.info("Iniciando extracción SECOP Socrata (endpoint=%s)", ENDPOINT)

        while True:
            page = self._fetch_page(last_id)
            if not page:
                break

            for raw in page:
                yield self._normalize_raw(raw)
                total_yielded += 1
                if self._max_records and total_yielded >= self._max_records:
                    logger.info("Límite de registros alcanzado (%d).", self._max_records)
                    return

            if len(page) < PAGE_SIZE:
                break  # última página

            last_id = page[-1].get(":id")
            logger.debug("Página procesada (last_id=%s, registros=%d)", last_id, len(page))
            time.sleep(PAGE_DELAY)

        logger.info("Extracción finalizada: %d registros extraídos.", total_yielded)

    @staticmethod
    def _normalize_raw(raw: dict) -> dict:
        """Mapea los campos Socrata a la interfaz interna del pipeline."""
        return {
            "entidad": (raw.get("nombre_entidad") or "").strip(),
            "contratista": (raw.get("proveedor_adjudicado") or "").strip(),
            "valor": raw.get("valor_del_contrato"),
            "fecha": raw.get("fecha_de_firma"),
            "estado": (raw.get("estado_contrato") or "").strip(),
            "identificacion_proveedor": (raw.get("documento_proveedor") or "").strip(),
            "proceso_de_compra": (raw.get("proceso_de_compra") or "").strip(),
            "fuente": SecopSocrataExtractor.SOURCE_NAME,
            "_raw": raw,  # payload original para rejected_records
            "_updated_at": raw.get(":updated_at"),  # para el cursor incremental por ventana
        }
