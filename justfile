# Claude Skill Manager - Development Commands

# Install all dependencies
install:
    uv sync --all-extras
    cd apps/web && npm install

# Run the API server
api:
    PYTHONPATH=packages/core:packages/connectors:packages/agents uv run uvicorn apps.api.main:app --reload --host 127.0.0.1 --port 8000

# Run the web UI dev server
web:
    cd apps/web && npm run dev

# Run the CLI
cli *ARGS:
    PYTHONPATH=packages/core:packages/connectors:packages/agents uv run python -m apps.cli.main {{ARGS}}

# Run tests
test:
    PYTHONPATH=packages/core:packages/connectors:packages/agents uv run pytest tests/ -v

# Run tests with coverage
test-cov:
    PYTHONPATH=packages/core:packages/connectors:packages/agents uv run pytest tests/ -v --cov=packages --cov-report=term-missing

# Run linting
lint:
    uv run ruff check .
    uv run ruff format --check .

# Fix lint issues
lint-fix:
    uv run ruff check --fix .
    uv run ruff format .

# Run type checking
typecheck:
    PYTHONPATH=packages/core:packages/connectors:packages/agents uv run mypy packages/core/csm_core/

# Run a scout pass
scout:
    PYTHONPATH=packages/core:packages/connectors:packages/agents uv run python -m apps.cli.main scout

# Generate proposals
propose:
    PYTHONPATH=packages/core:packages/connectors:packages/agents uv run python -m apps.cli.main propose

# Show registry status
status:
    PYTHONPATH=packages/core:packages/connectors:packages/agents uv run python -m apps.cli.main status

# Create a snapshot
snapshot:
    PYTHONPATH=packages/core:packages/connectors:packages/agents uv run python -m apps.cli.main snapshot

# Export registry graph
graph:
    PYTHONPATH=packages/core:packages/connectors:packages/agents uv run python -m apps.cli.main graph

# Run everything (API + Web) - use with tmux or separate terminals
serve:
    @echo "Start in two terminals:"
    @echo "  Terminal 1: just api"
    @echo "  Terminal 2: just web"

# Seed demo data (registry already has seed data)
seed:
    @echo "Registry is pre-seeded. Run 'just status' to verify."

# Clean generated artifacts
clean:
    rm -rf snapshots/*
    rm -rf registry/proposals/*.yaml
    rm -rf registry/evaluations/*.yaml
    rm -f graph.json
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
