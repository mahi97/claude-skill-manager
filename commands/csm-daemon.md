---
description: "Start the CSM daemon loop — persistent background scouting and management"
argument-hint: "[--max-iterations N] [--scout-interval N]"
allowed-tools: ["Bash(${CLAUDE_PLUGIN_ROOT}/hooks/scripts/daemon-setup.sh:*)", "Read", "Write", "Edit", "Bash", "Agent", "Grep", "Glob", "WebSearch", "WebFetch"]
---

# Start CSM Daemon

Initialize the persistent CSM daemon loop.

```!
"${CLAUDE_PLUGIN_ROOT}/hooks/scripts/daemon-setup.sh" $ARGUMENTS
```

After setup, read the state file and begin the daemon cycle:

1. Read `${CLAUDE_PLUGIN_ROOT}/.claude/csm-daemon.local.md` for your state
2. Check `${CLAUDE_PLUGIN_ROOT}/.claude/requests/` for any pending user requests
3. Handle pending requests first (search, suggest, build, etc.)
4. If no requests, do background work based on iteration number:
   - Iterations divisible by scout_interval: run a scout pass
   - Other iterations: evaluate candidates or generate proposals
5. Update the state file with results
6. When done with this iteration's work, stop (the Stop hook will bring you back)

Use the Python engine for registry operations:
```bash
cd "${CLAUDE_PLUGIN_ROOT}" && PYTHONPATH=packages/core:packages/connectors:packages/agents python3 -m apps.cli.main <command>
```
