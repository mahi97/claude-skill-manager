#!/usr/bin/env bash
# Bridge between CSM and divan CLI
# Usage: divan-bridge.sh <add|remove|sync|status|list> [args...]

set -euo pipefail

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"
DIVAN_BIN="${HOME}/divan/divan"
ACTION="${1:-help}"
shift || true

# Verify divan exists
if [[ ! -x "$DIVAN_BIN" ]]; then
    echo "ERROR: divan not found at $DIVAN_BIN"
    exit 1
fi

# Find the project root (where .divan.yaml is)
find_project_root() {
    local dir="$PWD"
    while [[ "$dir" != "/" ]]; do
        if [[ -f "$dir/.divan.yaml" ]]; then
            echo "$dir"
            return 0
        fi
        dir="$(dirname "$dir")"
    done
    echo ""
}

PROJECT_ROOT=$(find_project_root)
if [[ -z "$PROJECT_ROOT" ]]; then
    echo "WARNING: No .divan.yaml found in parent directories."
    echo "Divan operations may fail. Run from a divan-initialized project."
fi

case "$ACTION" in
    add)
        PLUGIN_NAME="$1"
        echo "Adding via divan: $PLUGIN_NAME"
        cd "${PROJECT_ROOT:-.}" && "$DIVAN_BIN" add "$PLUGIN_NAME"
        echo "Done. Restart Claude Code to activate."
        ;;
    remove)
        PLUGIN_NAME="$1"
        echo "Removing via divan: $PLUGIN_NAME"
        cd "${PROJECT_ROOT:-.}" && "$DIVAN_BIN" remove "$PLUGIN_NAME"
        echo "Done. Restart Claude Code to deactivate."
        ;;
    sync)
        echo "Syncing divan..."
        cd "${PROJECT_ROOT:-.}" && "$DIVAN_BIN" sync
        ;;
    status)
        cd "${PROJECT_ROOT:-.}" && "$DIVAN_BIN" status
        ;;
    list)
        "$DIVAN_BIN" list "$@"
        ;;
    help|*)
        echo "CSM Divan Bridge"
        echo "  add <plugin>     Add a plugin via divan"
        echo "  remove <plugin>  Remove a plugin via divan"
        echo "  sync             Re-sync from divan profile"
        echo "  status           Show divan project status"
        echo "  list             Browse available plugins"
        ;;
esac
