#!/usr/bin/env bash
# CSM post-install — called by divan after plugin installation
# Sets up deps and puts csm on PATH so it works immediately from any terminal

set -euo pipefail

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")" && pwd)}"

echo "  Setting up Claude Skill Manager..."

# Install uv if missing
if ! command -v uv &>/dev/null; then
    echo "  Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh 2>/dev/null
    export PATH="${HOME}/.local/bin:${PATH}"
fi

# Install Python deps
if [[ ! -d "${PLUGIN_ROOT}/.venv" ]]; then
    echo "  Installing Python dependencies..."
    cd "$PLUGIN_ROOT" && uv sync --all-extras --quiet 2>&1
fi

# Symlink csm to PATH
mkdir -p "${HOME}/.local/bin"
ln -sf "${PLUGIN_ROOT}/scripts/csm" "${HOME}/.local/bin/csm"

# Mark deps as installed (for SessionStart hook to skip)
mkdir -p "${PLUGIN_ROOT}/.claude"
date -u +"%Y-%m-%dT%H:%M:%SZ" > "${PLUGIN_ROOT}/.claude/.deps-installed"

echo "  CSM ready. Run: csm start"
