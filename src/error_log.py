"""Registro de errores del pipeline en formato Markdown.

Uso como context manager en pipeline.py:
    with PipelineErrorLog() as err:
        err.log("Extracción", "timeout en offset=3000")
        ...
Al salir escribe (o append) en errors.md. Las excepciones no capturadas
también quedan registradas antes de re-lanzarse.
"""

import logging
from datetime import datetime
from pathlib import Path

ERRORS_FILE = Path(__file__).parent.parent / "errors.md"

logger = logging.getLogger(__name__)

_HEADER = (
    "# ContrataData — Registro de Errores\n\n"
    "> Generado automáticamente por el pipeline ETL. No versionar (`errors.md` en `.gitignore`).\n"
)


def _ensure_file() -> None:
    if not ERRORS_FILE.exists():
        ERRORS_FILE.write_text(_HEADER, encoding="utf-8")


class PipelineErrorLog:
    """Acumula errores de una ejecución y los persiste al cerrar."""

    def __init__(self) -> None:
        self._run_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._sections: dict[str, list[str]] = {}

    def log(self, section: str, message: str) -> None:
        self._sections.setdefault(section, []).append(message)
        logger.warning("[error_log/%s] %s", section, message)

    def flush(self) -> None:
        if not any(self._sections.values()):
            return
        lines: list[str] = [f"\n## {self._run_ts}\n\n"]
        for section, entries in self._sections.items():
            lines.append(f"### {section}\n\n")
            for entry in entries:
                lines.append(f"- {entry}\n")
            lines.append("\n")
        _ensure_file()
        with ERRORS_FILE.open("a", encoding="utf-8") as fh:
            fh.writelines(lines)

    def __enter__(self) -> "PipelineErrorLog":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_type:
            self.log(
                "Excepción no capturada",
                f"`{exc_type.__name__}`: {exc_val}",
            )
        self.flush()
        return False
