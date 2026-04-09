#!/usr/bin/env bash
# CSM Daemon Stop Hook — keeps the daemon session alive
# Modeled on ralph-loop's Stop hook pattern

set -euo pipefail

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"
STATE_FILE="${PLUGIN_ROOT}/.claude/csm-daemon.local.md"

# If state file doesn't exist or daemon is not active, let the session exit
if [[ ! -f "$STATE_FILE" ]]; then
    exit 0
fi

# Read state
ACTIVE=$(grep '^active:' "$STATE_FILE" | head -1 | awk '{print $2}')
if [[ "$ACTIVE" != "true" ]]; then
    exit 0
fi

# Read iteration
ITERATION=$(grep '^iteration:' "$STATE_FILE" | head -1 | awk '{print $2}')
MAX_ITERATIONS=$(grep '^max_iterations:' "$STATE_FILE" | head -1 | awk '{print $2}')

# Validate numbers
if ! [[ "$ITERATION" =~ ^[0-9]+$ ]]; then
    ITERATION=1
fi
if ! [[ "$MAX_ITERATIONS" =~ ^[0-9]+$ ]]; then
    MAX_ITERATIONS=0
fi

# Check max iterations (0 = unlimited)
if [[ "$MAX_ITERATIONS" -gt 0 && "$ITERATION" -ge "$MAX_ITERATIONS" ]]; then
    # Deactivate and let session end
    sed -i 's/^active: true/active: false/' "$STATE_FILE"
    exit 0
fi

# Check for explicit stop request
STOP_REQUESTED=$(grep '^stop_requested:' "$STATE_FILE" | head -1 | awk '{print $2}')
if [[ "$STOP_REQUESTED" == "true" ]]; then
    sed -i 's/^active: true/active: false/' "$STATE_FILE"
    exit 0
fi

# Increment iteration
NEW_ITERATION=$((ITERATION + 1))
sed -i "s/^iteration: ${ITERATION}/iteration: ${NEW_ITERATION}/" "$STATE_FILE"

# Update last_tick
CURRENT_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
if grep -q '^last_tick:' "$STATE_FILE"; then
    sed -i "s|^last_tick:.*|last_tick: ${CURRENT_TIME}|" "$STATE_FILE"
else
    sed -i "/^iteration:/a last_tick: ${CURRENT_TIME}" "$STATE_FILE"
fi

# Read the phase/prompt from state file body (everything after second ---)
PROMPT=$(awk 'BEGIN{c=0} /^---$/{c++; next} c>=2{print}' "$STATE_FILE")

if [[ -z "$PROMPT" ]]; then
    PROMPT="Continue CSM daemon cycle. Check state file, handle any pending requests, then do background work (scout/evaluate/propose). Be brief."
fi

# Block the exit and feed prompt back
cat <<EOF
{
  "decision": "block",
  "reason": "SAME_PROMPT",
  "systemMessage": "CSM Daemon iteration ${NEW_ITERATION} | Phase: background | To stop: /csm-stop"
}
EOF
