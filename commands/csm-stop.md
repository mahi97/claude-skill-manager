---
description: "Stop the CSM daemon loop gracefully"
---

# Stop CSM Daemon

Set `stop_requested: true` in the daemon state file to stop the loop after the current iteration.

```bash
STATE_FILE="${CLAUDE_PLUGIN_ROOT}/.claude/csm-daemon.local.md"
if [ -f "$STATE_FILE" ]; then
    sed -i 's/^stop_requested: false/stop_requested: true/' "$STATE_FILE"
    sed -i 's/^active: true/active: false/' "$STATE_FILE"
    echo "CSM daemon stop requested. Will exit after current iteration."
else
    echo "No active daemon state found."
fi
```
