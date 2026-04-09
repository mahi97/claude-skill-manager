"""SkillHub connector - fetches skills from skillhub.club API."""

from __future__ import annotations

import os
from datetime import datetime, timezone

import httpx

from csm_core.models import (
    Category,
    ItemStatus,
    ItemType,
    RegistryItem,
    RiskAssessment,
    Source,
    TrustTier,
)

from .base import SourceConnector

SKILLHUB_API = "https://www.skillhub.club/api/v1"

# Map SkillHub categories to our taxonomy
CATEGORY_MAP = {
    "development": Category.CODING,
    "frontend": Category.UI,
    "backend": Category.CODING,
    "data": Category.SCIENTIFIC,
    "ai/ml": Category.SCIENTIFIC,
    "ai-ml": Category.SCIENTIFIC,
    "productivity": Category.CODING,
    "writing": Category.DOCS,
    "devops": Category.DEVOPS,
    "testing": Category.QUALITY,
    "documentation": Category.DOCS,
    "security": Category.INFRA,
    "research": Category.RESEARCH_AUTOMATION,
}


class SkillHubConnector(SourceConnector):
    """Fetches skills from SkillHub marketplace API."""

    def __init__(self, source: Source):
        super().__init__(source)
        self.api_key = os.environ.get("SKILLHUB_API_KEY", "")

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["x-api-key"] = self.api_key
        return headers

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{SKILLHUB_API}/skills/catalog",
                    headers=self._headers(),
                    params={"limit": 1},
                    timeout=10.0,
                )
                return resp.status_code == 200
        except httpx.HTTPError:
            return False

    async def fetch(self) -> list[RegistryItem]:
        items: list[RegistryItem] = []
        try:
            async with httpx.AsyncClient() as client:
                # Fetch catalog in batches
                for offset in range(0, 200, 50):
                    resp = await client.get(
                        f"{SKILLHUB_API}/skills/catalog",
                        headers=self._headers(),
                        params={
                            "limit": 50,
                            "offset": offset,
                            "sort": "composite",
                        },
                        timeout=30.0,
                    )
                    if resp.status_code != 200:
                        break

                    data = resp.json()
                    skills = data if isinstance(data, list) else data.get("skills", data.get("items", []))

                    if not skills:
                        break

                    for skill in skills:
                        item = self._normalize(skill)
                        if item:
                            items.append(item)

        except httpx.HTTPError:
            pass

        return items

    async def search(self, query: str, limit: int = 20) -> list[RegistryItem]:
        """Search SkillHub for skills matching a query."""
        items: list[RegistryItem] = []
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{SKILLHUB_API}/skills/search",
                    headers=self._headers(),
                    json={
                        "query": query,
                        "limit": limit,
                        "method": "hybrid",
                    },
                    timeout=15.0,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    skills = data if isinstance(data, list) else data.get("skills", data.get("results", []))
                    for skill in skills:
                        item = self._normalize(skill)
                        if item:
                            items.append(item)
        except httpx.HTTPError:
            pass

        return items

    def _normalize(self, skill: dict) -> RegistryItem | None:
        name = skill.get("name", "")
        if not name:
            return None

        # Determine categories
        cats = []
        raw_cat = skill.get("category", "").lower()
        if raw_cat in CATEGORY_MAP:
            cats.append(CATEGORY_MAP[raw_cat])
        for tag in skill.get("tags", []):
            tag_lower = tag.lower()
            if tag_lower in CATEGORY_MAP:
                cats.append(CATEGORY_MAP[tag_lower])

        # Determine trust tier based on score/stars
        score = skill.get("score", 0)
        stars = skill.get("stars", 0)
        if score >= 9.0 or stars >= 1000:
            trust = TrustTier.CURATED
        elif score >= 7.0 or stars >= 100:
            trust = TrustTier.COMMUNITY
        else:
            trust = TrustTier.COMMUNITY

        # Build source URL
        author = skill.get("author", "")
        slug = skill.get("slug", name)
        source_url = f"https://www.skillhub.club/skills/{author}-{slug}" if author else f"https://www.skillhub.club/skills/{slug}"

        return RegistryItem(
            id=f"skillhub-{slug}",
            name=name,
            type=ItemType.SKILL,
            description=skill.get("description", ""),
            source_url=source_url,
            repo_url=skill.get("repo_url", skill.get("repository", "")),
            version=skill.get("version", ""),
            categories=cats or [Category.CODING],
            trust_tier=trust,
            risk=RiskAssessment(flags=[], score=0.1),
            status=ItemStatus.CANDIDATE,
            last_seen_at=datetime.now(timezone.utc),
            metadata={
                "source_connector": "skillhub",
                "skillhub_score": score,
                "skillhub_stars": stars,
                "skillhub_author": author,
                "skillhub_category": raw_cat,
            },
        )
