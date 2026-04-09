#!/usr/bin/env bash
# CSM Daemon Setup — initialize or resume the daemon state file
# Called by /csm-daemon command to start the persistent loop

set -euo pipefail

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"
STATE_DIR="${PLUGIN_ROOT}/.claude"
STATE_FILE="${STATE_DIR}/csm-daemon.local.md"

mkdir -p "$STATE_DIR"

# Parse arguments
MAX_ITERATIONS=0  # 0 = unlimited
SCOUT_INTERVAL=10  # iterations between scout cycles

while [[ $# -gt 0 ]]; do
    case $1 in
        --max-iterations) MAX_ITERATIONS="$2"; shift 2 ;;
        --scout-interval) SCOUT_INTERVAL="$2"; shift 2 ;;
        *) shift ;;
    esac
done

SESSION_ID=$(uuidgen 2>/dev/null || python3 -c "import uuid; print(uuid.uuid4())")
CURRENT_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Check if already running
if [[ -f "$STATE_FILE" ]]; then
    EXISTING_ACTIVE=$(grep '^active:' "$STATE_FILE" | head -1 | awk '{print $2}')
    if [[ "$EXISTING_ACTIVE" == "true" ]]; then
        echo "CSM Daemon is already active. Reading existing state."
        cat "$STATE_FILE"
        exit 0
    fi
fi

# Create fresh state file
cat > "$STATE_FILE" <<HEREDOC
---
active: true
iteration: 1
max_iterations: ${MAX_ITERATIONS}
scout_interval: ${SCOUT_INTERVAL}
session_id: ${SESSION_ID}
started_at: ${CURRENT_TIME}
last_tick: ${CURRENT_TIME}
phase: idle
stop_requested: false
pending_requests: []
last_scout_summary: null
---

You are the CSM Daemon. Read your state above. Run your iteration cycle:
1. Check for pending user requests in the state file and handle them first
2. If no requests, check the phase and do background work:
   - Every ${SCOUT_INTERVAL} iterations: scout a source
   - Otherwise: evaluate unevaluated candidates, or generate proposals
3. Update the state file with your findings
4. Be brief in output — you're a background process

Use the Python engine for heavy lifting:
  PYTHONPATH=\${CLAUDE_PLUGIN_ROOT}/packages/core:\${CLAUDE_PLUGIN_ROOT}/packages/connectors:\${CLAUDE_PLUGIN_ROOT}/packages/agents

Key commands:
  python -m apps.cli.main status
  python -m apps.cli.main scout
  python -m apps.cli.main evaluate
  python -m apps.cli.main propose
  python -m apps.cli.main search <query>
HEREDOC

echo "CSM Daemon initialized. Session: ${SESSION_ID}"
echo "Max iterations: ${MAX_ITERATIONS} (0=unlimited)"
echo "Scout interval: every ${SCOUT_INTERVAL} iterations"
