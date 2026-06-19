"""Interfaz común para todos los adaptadores de extracción."""

from abc import ABC, abstractmethod
from typing import Iterator


class BaseExtractor(ABC):
    """Todo adaptador de fuente implementa este protocolo.

    Cada llamada a extract() debe producir dicts con al menos:
        entidad, contratista, valor, fecha, estado, fuente
    """

    SOURCE_NAME: str = ""

    @abstractmethod
    def extract(self) -> Iterator[dict]:
        """Yield registros crudos uno a uno."""
        ...
