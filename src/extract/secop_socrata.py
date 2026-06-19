"""Adaptador de extracción: SECOP II via API SODA (datos.gov.co).

Dataset: "SECOP II - Contratos Electrónicos"
Endpoint: https://www.datos.gov.co/resource/jbjy-vk9h.json

Documentación SODA: https://dev.socrata.com/consumers/getting-started.html
"""

import logging
import os
import time
from typing import Iterator

import requests

from src.extract.base import BaseExtractor

logger = logging.getLogger(__name__)

ENDPOINT = "https://www.datos.gov.co/resource/jbjy-vk9h.json"
PAGE_SIZE = 1000
MAX_RETRIES = 3
BACKOFF_SECONDS = 5


class SecopSocrataExtractor(BaseExtractor):
    SOURCE_NAME = "SECOP_SOCRATA"

    def __init__(self, app_token: str | None = None, max_records: int | None = None):
        self._app_token = app_token or os.getenv("SOCRATA_APP_TOKEN")
        self._max_records = max_records  # None = sin límite (dataset completo)

    def _build_headers(self) -> dict:
        headers = {"Accept": "application/json"}
        if self._app_token:
            headers["X-App-Token"] = self._app_token
        return headers

    def _fetch_page(self, offset: int) -> list[dict]:
        params = {
            "$limit": PAGE_SIZE,
            "$offset": offset,
            "$select": (
                "nombre_entidad,"
                "proveedor_adjudicado,"
                "valor_del_contrato,"
                "fecha_de_firma,"
                "estado_contrato,"
                "proceso_de_compra,"
                "identificacion_proveedor,"
                "nit_entidad"
            ),
            "$order": ":id",
        }
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                resp = requests.get(
                    ENDPOINT,
                    headers=self._build_headers(),
                    params=params,
                    timeout=30,
                )
                resp.raise_for_status()
                return resp.json()
            except requests.RequestException as exc:
                logger.warning(
                    "Intento %d/%d fallido (offset=%d): %s",
                    attempt, MAX_RETRIES, offset, exc,
                )
                if attempt < MAX_RETRIES:
                    time.sleep(BACKOFF_SECONDS * attempt)
        logger.error("Se agotaron los reintentos en offset=%d", offset)
        return []

    def extract(self) -> Iterator[dict]:
        offset = 0
        total_yielded = 0

        logger.info("Iniciando extracción SECOP Socrata (endpoint=%s)", ENDPOINT)

        while True:
            page = self._fetch_page(offset)
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

            offset += PAGE_SIZE
            logger.debug("Página procesada (offset=%d, registros=%d)", offset, len(page))

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
            "fuente": SecopSocrataExtractor.SOURCE_NAME,
            "_raw": raw,  # payload original para rejected_records
        }
