"""Domain models for Claude Skill Manager."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# --- Enums ---


class ItemType(str, Enum):
    SKILL = "skill"
    PLUGIN = "plugin"
    HOOK = "hook"
    MCP_SERVER = "mcp_server"
    SUBAGENT = "subagent"
    MARKETPLACE = "marketplace"
    SOURCE_REPO = "source_repo"


class ItemStatus(str, Enum):
    INSTALLED = "installed"
    CANDIDATE = "candidate"
    REJECTED = "rejected"
    DEPRECATED = "deprecated"
    PROPOSED = "proposed"


class TrustTier(str, Enum):
    OFFICIAL = "official"
    CURATED = "curated"
    COMMUNITY = "community"
    UNTRUSTED = "untrusted"


class RelationshipType(str, Enum):
    DEPENDS_ON = "depends_on"
    INSTALLED_FROM = "installed_from"
    CONFLICTS_WITH = "conflicts_with"
    SUPERSEDES = "supersedes"
    RECOMMENDED_WITH = "recommended_with"
    OBSERVED_BY = "observed_by"
    DEPRECATED_BY = "deprecated_by"


class Category(str, Enum):
    MEMORY = "memory"
    CODING = "coding"
    SCIENTIFIC = "scientific"
    DEVOPS = "devops"
    DOCS = "docs"
    REVIEW = "review"
    RESEARCH_AUTOMATION = "research-automation"
    INFRA = "infra"
    QUALITY = "quality"
    UI = "ui"


class RiskFlag(str, Enum):
    SHELL_EXECUTION = "shell_execution"
    NETWORK_CALLS = "network_calls"
    EXTERNAL_MCP_ACCESS = "external_mcp_access"
    WIDE_FILESYSTEM_ACCESS = "wide_filesystem_access"
    OPAQUE_INSTALL_METHOD = "opaque_install_method"
    LOW_REPO_ACTIVITY = "low_repo_activity"
    MISSING_DOCS = "missing_docs"
    MISSING_LICENSE = "missing_license"


class ProposalAction(str, Enum):
    INSTALL = "install"
    UPGRADE = "upgrade"
    REPLACE = "replace"
    REJECT = "reject"
    REMOVE = "remove"


class ProposalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    APPLIED = "applied"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


class SourceType(str, Enum):
    GITHUB_REPO = "github_repo"
    GITHUB_RELEASES = "github_releases"
    MARKETPLACE_JSON = "marketplace_json"
    LOCAL_DIRECTORY = "local_directory"
    SKILLHUB = "skillhub"


# --- Core Models ---


class Relationship(BaseModel):
    """A typed edge between two registry items."""

    source_id: str
    target_id: str
    type: RelationshipType
    notes: str = ""


class RiskAssessment(BaseModel):
    """Risk profile for a registry item."""

    flags: list[RiskFlag] = Field(default_factory=list)
    score: float = Field(default=0.0, ge=0.0, le=1.0)
    notes: str = ""


class RegistryItem(BaseModel):
    """A component in the Claude Code ecosystem."""

    id: str
    name: str
    type: ItemType
    description: str = ""
    source_url: str = ""
    repo_url: str = ""
    version: str = ""
    categories: list[Category] = Field(default_factory=list)
    trust_tier: TrustTier = TrustTier.UNTRUSTED
    risk: RiskAssessment = Field(default_factory=RiskAssessment)
    status: ItemStatus = ItemStatus.CANDIDATE
    last_seen_at: datetime | None = None
    last_evaluated_at: datetime | None = None
    local_notes: str = ""
    relationships: list[Relationship] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Source(BaseModel):
    """A trusted or tracked source for discovering components."""

    id: str
    name: str
    type: SourceType
    url: str
    trust_tier: TrustTier = TrustTier.COMMUNITY
    enabled: bool = True
    last_synced_at: datetime | None = None
    sync_interval_hours: int = 24
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvaluationScore(BaseModel):
    """Individual evaluation dimension."""

    dimension: str
    score: float = Field(ge=0.0, le=1.0)
    weight: float = Field(default=1.0, ge=0.0)
    reasoning: str = ""


class EvaluationReport(BaseModel):
    """Evaluation of a candidate item."""

    id: str
    item_id: str
    scores: list[EvaluationScore] = Field(default_factory=list)
    overall_score: float = Field(default=0.0, ge=0.0, le=1.0)
    recommendation: str = ""
    overlap_with: list[str] = Field(default_factory=list)
    risk_assessment: RiskAssessment = Field(default_factory=RiskAssessment)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    evaluator: str = "deterministic-v1"


class ProposalChange(BaseModel):
    """A single change within a proposal."""

    action: ProposalAction
    item_id: str
    item_name: str
    description: str = ""
    registry_diff: dict[str, Any] = Field(default_factory=dict)


class Proposal(BaseModel):
    """A structured change proposal for the registry."""

    id: str
    title: str
    summary: str = ""
    changes: list[ProposalChange] = Field(default_factory=list)
    why_it_matters: str = ""
    overlap_analysis: str = ""
    trust_summary: str = ""
    risk_summary: str = ""
    workflow_impact: str = ""
    recommendation: str = ""
    status: ProposalStatus = ProposalStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    applied_at: datetime | None = None
    snapshot_id: str | None = None


class Snapshot(BaseModel):
    """A point-in-time registry snapshot."""

    id: str
    description: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    trigger: str = ""  # e.g., "pre-apply:proposal-001"
    file_manifest: list[str] = Field(default_factory=list)


class TaxonomyNode(BaseModel):
    """A node in the taxonomy tree."""

    id: str
    name: str
    parent_id: str | None = None
    description: str = ""
    children: list[str] = Field(default_factory=list)


class PolicyRule(BaseModel):
    """A policy rule governing auto-behavior."""

    id: str
    name: str
    description: str = ""
    condition: str = ""  # e.g., "trust_tier == 'untrusted'"
    action: str = ""  # e.g., "block_auto_install"
    enabled: bool = True
