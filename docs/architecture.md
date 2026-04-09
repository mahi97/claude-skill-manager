# Architecture

## Overview

Claude Skill Manager (CSM) is a local-first monorepo with three application layers and three shared packages.

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   Web UI    │  │    CLI      │  │   API       │
│  React/Vite │  │   Typer     │  │  FastAPI    │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │
       └────────────────┼────────────────┘
                        │
       ┌────────────────┼────────────────┐
       │                │                │
┌──────┴──────┐  ┌──────┴──────┐  ┌──────┴──────┐
│   Agents    │  │    Core     │  │ Connectors  │
│  Pipeline   │  │  Models     │  │  GitHub     │
│  Scout      │  │  Registry   │  │  Local      │
│  Apply      │  │  Evaluator  │  │  Marketplace│
│             │  │  Proposer   │  │             │
│             │  │  Graph      │  │             │
│             │  │  Diff       │  │             │
└─────────────┘  └─────────────┘  └─────────────┘
                        │
                 ┌──────┴──────┐
                 │  Registry   │
                 │  YAML files │
                 │  (source of │
                 │   truth)    │
                 └─────────────┘
```

## Components

### Applications

**API (`apps/api/`)**: FastAPI server exposing REST endpoints for all registry operations. Serves as the backend for the web UI and can be used by any HTTP client. Stateless — all state lives in the registry YAML files.

**CLI (`apps/cli/`)**: Typer-based terminal interface. Imports the same core/agents/connectors packages as the API. Designed for fast interactive use.

**Web (`apps/web/`)**: React + TypeScript + Vite SPA. Fetches data from the API via TanStack Query. Uses React Flow for graph visualization and Tailwind CSS for styling. Proxies `/api` to the backend in development.

### Packages

**Core (`packages/core/csm_core/`)**: The heart of the system.
- `models.py`: Pydantic domain models — RegistryItem, Source, Proposal, Evaluation, Snapshot, etc.
- `registry.py`: Registry and SnapshotManager classes. All YAML I/O and CRUD operations.
- `evaluator.py`: Deterministic evaluator with pluggable dimensions (freshness, docs, trust, risk, overlap).
- `proposer.py`: Generates structured Proposal objects from evaluation reports.
- `graph.py`: NetworkX-based graph construction and JSON export for visualization.
- `diff.py`: Item and state diffing for comparisons and proposal rendering.

**Connectors (`packages/connectors/csm_connectors/`)**: Source-specific data fetchers.
- `base.py`: Abstract `SourceConnector` interface.
- `local.py`: Scans local directories for plugin.json and skill markdown files.
- `github.py`: Fetches repository metadata via GitHub API.
- `marketplace.py`: Fetches from JSON marketplace endpoints.
- `factory.py`: Returns the right connector for a given source type.

**Agents (`packages/agents/csm_agents/`)**: Orchestration modules.
- `scout.py`: ScoutAgent — iterates sources, fetches via connectors, deduplicates.
- `pipeline.py`: PipelineAgent — orchestrates scout → evaluate → propose.
- `applier.py`: ApplyAgent — applies proposals with snapshot safety.

## Data Flow

```
Sources (GitHub, local, marketplace)
    │
    ▼
ScoutAgent.scout_all()
    │ discovers new items
    ▼
Registry.add_candidate()
    │ deduplicates, saves to candidates.yaml
    ▼
evaluate_item()
    │ scores on 5 dimensions
    ▼
generate_proposal()
    │ creates structured change proposal
    ▼
[User reviews proposal]
    │
    ▼
ApplyAgent.apply_proposal()
    │ creates snapshot, mutates registry
    ▼
Registry updated (installed/rejected)
```

## Design Decisions

1. **YAML registry as source of truth**: No database for the core registry. YAML files are human-readable, diffable, and version-controllable. SQLite is available for future metadata/caching but is not required for MVP.

2. **Proposal-driven changes**: Nothing is installed silently. Every change goes through the proposal pipeline, creating an auditable trail.

3. **Snapshot safety**: Every mutation creates a pre-mutation snapshot. Rollback is always possible.

4. **Modular evaluation**: The evaluator uses pluggable scoring dimensions. Adding Claude-powered evaluation means adding new dimension functions, not rewriting the evaluator.

5. **Connector abstraction**: New sources can be added by implementing the `SourceConnector` interface. The factory pattern keeps the scout agent source-agnostic.

6. **Agents as callable modules**: The agents package is structured for future Claude Agent SDK integration — each agent is a class with clear inputs and outputs.
