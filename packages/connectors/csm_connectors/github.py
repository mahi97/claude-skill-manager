"""GitHub connector - fetches plugin/skill metadata from GitHub repos."""

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
    RiskFlag,
    Source,
    TrustTier,
)

from .base import SourceConnector

GITHUB_API = "https://api.github.com"


class GitHubRepoConnector(SourceConnector):
    """Fetches metadata from a GitHub repository."""

    def __init__(self, source: Source):
        super().__init__(source)
        self.token = os.environ.get("GITHUB_TOKEN", "")
        self._owner, self._repo = self._parse_repo_url(source.url)

    def _parse_repo_url(self, url: str) -> tuple[str, str]:
        parts = url.rstrip("/").split("/")
        if len(parts) >= 2:
            return parts[-2], parts[-1]
        return "", ""

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/vnd.github.v3+json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def health_check(self) -> bool:
        if not self._owner or not self._repo:
            return False
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{GITHUB_API}/repos/{self._owner}/{self._repo}",
                    headers=self._headers(),
                    timeout=10.0,
                )
                return resp.status_code == 200
        except httpx.HTTPError:
            return False

    async def fetch(self) -> list[RegistryItem]:
        if not self._owner or not self._repo:
            return []

        items: list[RegistryItem] = []
        try:
            async with httpx.AsyncClient() as client:
                # Get repo info
                repo_resp = await client.get(
                    f"{GITHUB_API}/repos/{self._owner}/{self._repo}",
                    headers=self._headers(),
                    timeout=10.0,
                )
                if repo_resp.status_code != 200:
                    return []
                repo_data = repo_resp.json()

                # Try to get directory listing for plugins/skills
                contents_resp = await client.get(
                    f"{GITHUB_API}/repos/{self._owner}/{self._repo}/contents",
                    headers=self._headers(),
                    timeout=10.0,
                )
                if contents_resp.status_code == 200:
                    contents = contents_resp.json()
                    for entry in contents:
                        if entry.get("type") == "dir":
                            item = self._make_item_from_dir(entry, repo_data)
                            if item:
                                items.append(item)

                # If no subdirectories found, treat the repo itself as an item
                if not items:
                    items.append(self._make_item_from_repo(repo_data))

        except httpx.HTTPError:
            # Graceful degradation - return empty on network errors
            pass

        return items

    def _make_item_from_repo(self, repo: dict) -> RegistryItem:
        risk_flags = []
        if not repo.get("license"):
            risk_flags.append(RiskFlag.MISSING_LICENSE)
        if not repo.get("description"):
            risk_flags.append(RiskFlag.MISSING_DOCS)

        pushed_at = repo.get("pushed_at")
        last_seen = datetime.fromisoformat(pushed_at.replace("Z", "+00:00")) if pushed_at else None

        stars = repo.get("stargazers_count", 0)
        if stars < 5:
            risk_flags.append(RiskFlag.LOW_REPO_ACTIVITY)

        return RegistryItem(
            id=f"gh-{self._owner}-{self._repo}",
            name=repo.get("name", self._repo),
            type=ItemType.PLUGIN,
            description=repo.get("description", ""),
            source_url=repo.get("html_url", ""),
            repo_url=repo.get("html_url", ""),
            version=repo.get("default_branch", "main"),
            categories=[Category.CODING],
            trust_tier=self.source.trust_tier,
            risk=RiskAssessment(flags=risk_flags, score=min(len(risk_flags) * 0.15, 1.0)),
            status=ItemStatus.CANDIDATE,
            last_seen_at=last_seen,
            metadata={
                "source_connector": "github_repo",
                "stars": stars,
                "forks": repo.get("forks_count", 0),
                "language": repo.get("language", ""),
            },
        )

    def _make_item_from_dir(self, entry: dict, repo: dict) -> RegistryItem | None:
        name = entry.get("name", "")
        if name.startswith(".") or name in ("node_modules", "__pycache__", "dist", "build"):
            return None

        return RegistryItem(
            id=f"gh-{self._owner}-{self._repo}-{name}",
            name=name,
            type=ItemType.PLUGIN,
            description=f"Component '{name}' from {self._owner}/{self._repo}",
            source_url=entry.get("html_url", ""),
            repo_url=repo.get("html_url", ""),
            version=repo.get("default_branch", "main"),
            categories=[Category.CODING],
            trust_tier=self.source.trust_tier,
            risk=RiskAssessment(flags=[], score=0.1),
            status=ItemStatus.CANDIDATE,
            last_seen_at=datetime.now(timezone.utc),
            metadata={
                "source_connector": "github_repo",
                "parent_repo": f"{self._owner}/{self._repo}",
            },
        )
