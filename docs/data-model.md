# Data Model

## Object Types

| Type | Description |
|------|-------------|
| `skill` | A Claude Code skill (markdown with frontmatter) |
| `plugin` | A Claude Code plugin (directory with plugin.json) |
| `hook` | A pre/post tool-use hook |
| `mcp_server` | An MCP (Model Context Protocol) server |
| `subagent` | A specialized subagent configuration |
| `marketplace` | A marketplace or registry endpoint |
| `source_repo` | A source repository containing components |

## Relationship Types

| Type | Description |
|------|-------------|
| `depends_on` | Item requires another item to function |
| `installed_from` | Item was installed from a source |
| `conflicts_with` | Items are incompatible or redundant |
| `supersedes` | Item replaces an older item |
| `recommended_with` | Items work well together |
| `observed_by` | Item was discovered by a source |
| `deprecated_by` | Item is deprecated in favor of another |

## Trust Tiers

| Tier | Description |
|------|-------------|
| `official` | From Anthropic or first-party sources |
| `curated` | Reviewed and approved by trusted maintainers |
| `community` | From community sources, not formally reviewed |
| `untrusted` | Unknown provenance, requires manual review |

## Risk Flags

| Flag | Description |
|------|-------------|
| `shell_execution` | Runs shell commands |
| `network_calls` | Makes network requests |
| `external_mcp_access` | Connects to external MCP servers |
| `wide_filesystem_access` | Reads/writes broadly on the filesystem |
| `opaque_install_method` | Install process is not transparent |
| `low_repo_activity` | Source repo has low activity |
| `missing_docs` | No or minimal documentation |
| `missing_license` | No license file found |

## Categories

`memory`, `coding`, `scientific`, `devops`, `docs`, `review`, `research-automation`, `infra`, `quality`, `ui`

## Core Schemas

### RegistryItem

The central model. Represents any component in the ecosystem.

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier |
| `name` | string | Human-readable name |
| `type` | ItemType | One of the object types above |
| `description` | string | What this item does |
| `source_url` | string | Where it was found |
| `repo_url` | string | Git repository URL |
| `version` | string | Version string |
| `categories` | Category[] | Taxonomy tags |
| `trust_tier` | TrustTier | Trust classification |
| `risk` | RiskAssessment | Risk flags and score |
| `status` | ItemStatus | installed/candidate/rejected/deprecated |
| `last_seen_at` | datetime | When last observed by scout |
| `last_evaluated_at` | datetime | When last evaluated |
| `local_notes` | string | User-added notes |
| `relationships` | Relationship[] | Typed edges to other items |
| `metadata` | dict | Arbitrary key-value data |
| `created_at` | datetime | When first added |
| `updated_at` | datetime | When last modified |

### Source

A configured discovery source.

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier |
| `name` | string | Human-readable name |
| `type` | SourceType | github_repo/marketplace_json/local_directory |
| `url` | string | Source location |
| `trust_tier` | TrustTier | Trust level for items from this source |
| `enabled` | bool | Whether scouting is active |
| `last_synced_at` | datetime | When last scouted |
| `sync_interval_hours` | int | Desired sync frequency |

### Proposal

A structured change proposal.

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier |
| `title` | string | Short title |
| `summary` | string | What this proposal does |
| `changes` | ProposalChange[] | List of individual changes |
| `why_it_matters` | string | Explanation of value |
| `overlap_analysis` | string | Overlap with current stack |
| `trust_summary` | string | Trust assessment |
| `risk_summary` | string | Risk assessment |
| `workflow_impact` | string | How this affects the user's workflow |
| `recommendation` | string | Evaluator recommendation |
| `status` | ProposalStatus | pending/approved/applied/rejected |
| `snapshot_id` | string | Pre-apply snapshot reference |

### EvaluationReport

Evaluation results for a candidate.

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier |
| `item_id` | string | Evaluated item reference |
| `scores` | EvaluationScore[] | Per-dimension scores |
| `overall_score` | float | Weighted aggregate (0-1) |
| `recommendation` | string | Human-readable recommendation |
| `overlap_with` | string[] | IDs of overlapping installed items |
| `risk_assessment` | RiskAssessment | Risk profile |
| `evaluator` | string | Evaluator version identifier |

### Snapshot

Point-in-time registry backup.

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Timestamped identifier |
| `description` | string | Why this snapshot was created |
| `trigger` | string | What caused it (pre-apply, manual, etc.) |
| `file_manifest` | string[] | List of files in the snapshot |
| `created_at` | datetime | When created |
