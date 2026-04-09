"""Connector factory - instantiate the right connector for a source."""

from __future__ import annotations

from csm_core.models import Source, SourceType

from .base import SourceConnector
from .github import GitHubRepoConnector
from .local import LocalDirectoryConnector
from .marketplace import MarketplaceConnector
from .skillhub import SkillHubConnector


def get_connector(source: Source) -> SourceConnector:
    """Return the appropriate connector for a source type."""
    match source.type:
        case SourceType.LOCAL_DIRECTORY:
            return LocalDirectoryConnector(source)
        case SourceType.GITHUB_REPO | SourceType.GITHUB_RELEASES:
            return GitHubRepoConnector(source)
        case SourceType.MARKETPLACE_JSON:
            return MarketplaceConnector(source)
        case SourceType.SKILLHUB:
            return SkillHubConnector(source)
        case _:
            raise ValueError(f"Unknown source type: {source.type}")
