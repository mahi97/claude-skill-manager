#!/usr/bin/env bash
# Queue a request to the CSM daemon from an external session
# Usage: queue-request.sh <action> [args...]
# Example: queue-request.sh search "memory plugin"
# Example: queue-request.sh suggest
# Example: queue-request.sh build "arxiv paper summarizer skill"

set -euo pipefail

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"
STATE_FILE="${PLUGIN_ROOT}/.claude/csm-daemon.local.md"
QUEUE_DIR="${PLUGIN_ROOT}/.claude/requests"

mkdir -p "$QUEUE_DIR"

ACTION="${1:-help}"
shift || true
ARGS="$*"

TIMESTAMP=$(date -u +"%Y%m%d-%H%M%S")
REQUEST_ID="req-${TIMESTAMP}-$$"

# Write request file
cat > "${QUEUE_DIR}/${REQUEST_ID}.yaml" <<EOF
id: ${REQUEST_ID}
action: ${ACTION}
args: "${ARGS}"
created_at: ${TIMESTAMP}
status: pending
EOF

echo "Request queued: ${REQUEST_ID}"
echo "  Action: ${ACTION}"
echo "  Args: ${ARGS}"
echo ""
echo "The daemon will pick this up on its next iteration."
echo "Check results in: ${PLUGIN_ROOT}/registry/ or attach to tmux session 'csm-daemon'"
