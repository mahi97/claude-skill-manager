"""Marketplace JSON connector - fetches items from a marketplace API endpoint."""

from __future__ import annotations

from datetime import datetime, timezone

import httpx

from csm_core.models import (
    Category,
    ItemStatus,
    ItemType,
    RegistryItem,
    RiskAssessment,
    Source,
)

from .base import SourceConnector

# Mapping from marketplace type strings to our ItemType
TYPE_MAP = {
    "skill": ItemType.SKILL,
    "plugin": ItemType.PLUGIN,
    "hook": ItemType.HOOK,
    "mcp_server": ItemType.MCP_SERVER,
    "mcp-server": ItemType.MCP_SERVER,
    "subagent": ItemType.SUBAGENT,
    "marketplace": ItemType.MARKETPLACE,
}

CATEGORY_MAP = {c.value: c for c in Category}


class MarketplaceConnector(SourceConnector):
    """Fetches items from a JSON marketplace endpoint."""

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.head(self.source.url, timeout=10.0)
                return resp.status_code < 400
        except httpx.HTTPError:
            return False

    async def fetch(self) -> list[RegistryItem]:
        items: list[RegistryItem] = []
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(self.source.url, timeout=30.0)
                if resp.status_code != 200:
                    return []
                data = resp.json()

            # Support both array and {"items": [...]} formats
            entries = data if isinstance(data, list) else data.get("items", data.get("plugins", []))

            for entry in entries:
                item = self._normalize(entry)
                if item:
                    items.append(item)

        except (httpx.HTTPError, ValueError):
            pass

        return items

    def _normalize(self, entry: dict) -> RegistryItem | None:
        name = entry.get("name", "")
        if not name:
            return None

        item_type = TYPE_MAP.get(entry.get("type", "plugin"), ItemType.PLUGIN)

        cats = []
        for tag in entry.get("categories", entry.get("tags", [])):
            if tag in CATEGORY_MAP:
                cats.append(CATEGORY_MAP[tag])

        return RegistryItem(
            id=f"mkt-{self.source.id}-{name}",
            name=name,
            type=item_type,
            description=entry.get("description", ""),
            source_url=entry.get("url", self.source.url),
            repo_url=entry.get("repo_url", ""),
            version=entry.get("version", ""),
            categories=cats or [Category.CODING],
            trust_tier=self.source.trust_tier,
            risk=RiskAssessment(flags=[], score=0.2),
            status=ItemStatus.CANDIDATE,
            last_seen_at=datetime.now(timezone.utc),
            metadata={
                "source_connector": "marketplace_json",
                "marketplace_source": self.source.id,
                "raw": entry,
            },
        )
