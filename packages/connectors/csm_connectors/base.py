"""Base connector interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from csm_core.models import RegistryItem, Source


class SourceConnector(ABC):
    """Abstract base for source connectors."""

    def __init__(self, source: Source):
        self.source = source

    @abstractmethod
    async def fetch(self) -> list[RegistryItem]:
        """Fetch items from this source. Returns normalized RegistryItems."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the source is reachable."""
        ...
