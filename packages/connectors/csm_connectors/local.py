"""Local directory connector - scans local plugin/skill directories."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import yaml

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


class LocalDirectoryConnector(SourceConnector):
    """Scans a local directory for Claude Code plugins and skills."""

    def __init__(self, source: Source):
        super().__init__(source)
        self.path = Path(source.url)

    async def health_check(self) -> bool:
        return self.path.exists() and self.path.is_dir()

    async def fetch(self) -> list[RegistryItem]:
        if not await self.health_check():
            return []

        items: list[RegistryItem] = []

        for entry in self.path.iterdir():
            if not entry.is_dir():
                continue

            # Check for plugin.json
            plugin_json = entry / "plugin.json"
            if plugin_json.exists():
                item = self._parse_plugin_json(entry, plugin_json)
                if item:
                    items.append(item)
                continue

            # Check for skill files (yaml frontmatter markdown)
            for skill_file in entry.glob("*.md"):
                item = self._parse_skill_file(entry, skill_file)
                if item:
                    items.append(item)

        return items

    def _parse_plugin_json(self, directory: Path, plugin_file: Path) -> RegistryItem | None:
        try:
            with open(plugin_file) as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            return None

        name = data.get("name", directory.name)
        risk_flags = []
        if data.get("hooks"):
            risk_flags.append(RiskFlag.SHELL_EXECUTION)

        return RegistryItem(
            id=f"local-{name}",
            name=name,
            type=ItemType.PLUGIN,
            description=data.get("description", ""),
            source_url=str(directory),
            version=data.get("version", "0.0.0"),
            categories=self._infer_categories(data),
            trust_tier=self.source.trust_tier,
            risk=RiskAssessment(flags=risk_flags, score=len(risk_flags) * 0.15),
            status=ItemStatus.CANDIDATE,
            last_seen_at=datetime.now(timezone.utc),
            metadata={"source_connector": "local_directory"},
        )

    def _parse_skill_file(self, directory: Path, skill_file: Path) -> RegistryItem | None:
        try:
            content = skill_file.read_text()
        except OSError:
            return None

        # Parse YAML frontmatter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                try:
                    frontmatter = yaml.safe_load(parts[1])
                except yaml.YAMLError:
                    frontmatter = {}
            else:
                frontmatter = {}
        else:
            frontmatter = {}

        name = frontmatter.get("name", skill_file.stem)
        return RegistryItem(
            id=f"local-skill-{name}",
            name=name,
            type=ItemType.SKILL,
            description=frontmatter.get("description", ""),
            source_url=str(skill_file),
            version="0.0.0",
            categories=self._infer_categories(frontmatter),
            trust_tier=self.source.trust_tier,
            risk=RiskAssessment(flags=[], score=0.05),
            status=ItemStatus.CANDIDATE,
            last_seen_at=datetime.now(timezone.utc),
            metadata={"source_connector": "local_directory"},
        )

    def _infer_categories(self, data: dict) -> list[Category]:
        """Simple heuristic category inference."""
        cats = []
        text = json.dumps(data).lower()
        if any(w in text for w in ["commit", "git", "deploy", "ci"]):
            cats.append(Category.DEVOPS)
        if any(w in text for w in ["review", "pr", "pull request"]):
            cats.append(Category.REVIEW)
        if any(w in text for w in ["test", "lint", "quality"]):
            cats.append(Category.QUALITY)
        if any(w in text for w in ["doc", "readme", "markdown"]):
            cats.append(Category.DOCS)
        if any(w in text for w in ["memory", "remember", "persist"]):
            cats.append(Category.MEMORY)
        if any(w in text for w in ["code", "develop", "implement"]):
            cats.append(Category.CODING)
        return cats or [Category.CODING]
