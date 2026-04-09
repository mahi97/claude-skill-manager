"""Scout agent - discovers new items from configured sources."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from csm_connectors.factory import get_connector
from csm_core.models import RegistryItem
from csm_core.registry import Registry

logger = logging.getLogger(__name__)


class ScoutAgent:
    """Scans configured sources for new Claude Code ecosystem components."""

    def __init__(self, registry: Registry):
        self.registry = registry

    async def scout_source(self, source_id: str) -> list[RegistryItem]:
        """Scout a single source by ID."""
        sources = self.registry.load_sources()
        source = next((s for s in sources if s.id == source_id), None)
        if not source:
            logger.warning(f"Source not found: {source_id}")
            return []

        if not source.enabled:
            logger.info(f"Source disabled: {source.name}")
            return []

        connector = get_connector(source)

        healthy = await connector.health_check()
        if not healthy:
            logger.warning(f"Source unreachable: {source.name} ({source.url})")
            return []

        logger.info(f"Scouting source: {source.name}")
        discovered = await connector.fetch()
        logger.info(f"Found {len(discovered)} items from {source.name}")

        new_items = []
        for item in discovered:
            added = self.registry.add_candidate(item)
            if added:
                new_items.append(item)
                logger.info(f"  New candidate: {item.name} ({item.type.value})")

        # Update source sync timestamp
        source.last_synced_at = datetime.now(timezone.utc)
        all_sources = self.registry.load_sources()
        for i, s in enumerate(all_sources):
            if s.id == source.id:
                all_sources[i] = source
                break
        self.registry.save_sources(all_sources)

        return new_items

    async def scout_all(self) -> dict[str, list[RegistryItem]]:
        """Scout all enabled sources."""
        sources = self.registry.load_sources()
        results: dict[str, list[RegistryItem]] = {}

        for source in sources:
            if source.enabled:
                try:
                    found = await self.scout_source(source.id)
                    results[source.id] = found
                except Exception as e:
                    logger.error(f"Error scouting {source.name}: {e}")
                    results[source.id] = []

        deduped = self.registry.deduplicate_candidates()
        if deduped:
            logger.info(f"Removed {deduped} duplicate candidates")

        return results
