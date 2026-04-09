#!/usr/bin/env bash
# Start the CSM daemon in a tmux session
# Usage: ./scripts/start-daemon.sh [--max-iterations N] [--scout-interval N]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SESSION_NAME="csm-daemon"

# Check if tmux session already exists
if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo "CSM daemon tmux session already exists."
    echo "Attach with: tmux attach -t $SESSION_NAME"
    echo "Or kill with: tmux kill-session -t $SESSION_NAME"
    exit 0
fi

# Create tmux session running Claude Code with the daemon command
tmux new-session -d -s "$SESSION_NAME" -c "$PLUGIN_ROOT" \
    "claude --dangerously-skip-permissions '/csm-daemon $*'"

echo "CSM daemon started in tmux session: $SESSION_NAME"
echo ""
echo "  Attach:    tmux attach -t $SESSION_NAME"
echo "  Detach:    Ctrl+B, D (inside tmux)"
echo "  Stop:      /csm-stop (inside session) or tmux kill-session -t $SESSION_NAME"
echo ""
echo "You can also talk to CSM from any Claude Code session using /csm commands."
