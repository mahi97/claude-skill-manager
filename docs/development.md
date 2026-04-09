# Development Guide

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- Node.js 20+ / npm
- [just](https://github.com/casey/just) (optional but recommended)

## Setup

```bash
# Clone and enter the repo
cd claude-skill-manager

# Install Python dependencies
uv sync --all-extras

# Install web UI dependencies
cd apps/web && npm install && cd ../..

# (Optional) Install pre-commit hooks
uv run pre-commit install
```

## Running Locally

```bash
# API server (port 8000)
just api

# Web UI (port 5173, proxies /api to backend)
just web

# CLI commands
just cli status
just cli search memory
just cli inspect plugin-superpowers
```

## Testing

```bash
just test           # Run all tests
just test-cov       # With coverage report
```

Tests use `tmp_path` fixtures to create isolated registries — they never touch the real `registry/` directory.

## Code Quality

```bash
just lint           # Ruff check + format check
just lint-fix       # Auto-fix
just typecheck      # mypy on core package
```

## Project Structure

```
apps/
  api/main.py         FastAPI application
  cli/main.py         Typer CLI application
  web/                React + Vite SPA
    src/
      components/     Shared UI components
      pages/          Page-level components
      lib/api.ts      API client

packages/
  core/csm_core/      Domain logic (no external deps besides pydantic/yaml/networkx)
  connectors/         Source connectors (httpx for network)
  agents/             Orchestration agents

registry/             Canonical YAML data
tests/                pytest suite
docs/                 Documentation
```

## Adding a New Connector

1. Create `packages/connectors/csm_connectors/myconnector.py`
2. Implement the `SourceConnector` interface (see `base.py`)
3. Add the source type to `models.py` `SourceType` enum
4. Register in `factory.py`
5. Add a source entry to `registry/sources.yaml`

## Adding an Evaluation Dimension

1. Add a function to `packages/core/csm_core/evaluator.py` following the pattern of `evaluate_freshness()`
2. Add it to the `evaluate_item()` function's scores list
3. Add tests in `tests/test_evaluator.py`

## Adding a CLI Command

1. Add a function to `apps/cli/main.py` decorated with `@app.command()`
2. Use the `console` object for Rich output
3. Import from core/agents packages as needed

## Adding an API Endpoint

1. Add a route function to `apps/api/main.py`
2. Use `get_registry()` / `get_snapshot_mgr()` for state access
3. Return Pydantic model dicts for JSON serialization
