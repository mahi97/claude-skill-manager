#!/usr/bin/env bash
# CSM SessionStart hook — auto-installs dependencies on first use
# Runs silently and quickly if deps are already installed

set -euo pipefail

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"
MARKER="${PLUGIN_ROOT}/.claude/.deps-installed"

# Skip if already set up
if [[ -f "$MARKER" ]]; then
    exit 0
fi

# Check for uv
if ! command -v uv &>/dev/null; then
    echo "CSM: uv not found. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh 2>/dev/null
    export PATH="${HOME}/.local/bin:${PATH}"
fi

# Install Python deps if needed
if [[ ! -d "${PLUGIN_ROOT}/.venv" ]]; then
    echo "CSM: Installing Python dependencies (first run)..."
    cd "$PLUGIN_ROOT" && uv sync --all-extras --quiet 2>&1
fi

# Verify core imports work
cd "$PLUGIN_ROOT"
PYTHONPATH="packages/core:packages/connectors:packages/agents" \
    uv run python -c "from csm_core.models import ItemType" 2>/dev/null || {
    echo "CSM: Dependency check failed, reinstalling..."
    uv sync --all-extras --quiet 2>&1
}

# Symlink csm to PATH if not already there
if ! command -v csm &>/dev/null; then
    mkdir -p "${HOME}/.local/bin"
    ln -sf "${PLUGIN_ROOT}/scripts/csm" "${HOME}/.local/bin/csm"
fi

# Mark as installed
mkdir -p "${PLUGIN_ROOT}/.claude"
date -u +"%Y-%m-%dT%H:%M:%SZ" > "$MARKER"

echo "CSM: Ready. Use /csm commands or 'csm' CLI."
