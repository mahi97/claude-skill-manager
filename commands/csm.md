---
description: "Claude Skill Manager — manage your Claude Code ecosystem. Use: /csm <action> [args]"
argument-hint: "<search|status|inspect|suggest|compare|propose|apply|scout|snapshot|rollback|build|stop> [args]"
---

# CSM — Claude Skill Manager

Route to the appropriate CSM action based on the first argument.

Parse `$ARGUMENTS` to determine the action:

## Actions

### `/csm status`
Show the current registry status — installed count, candidates, proposals, sources, snapshots.
Run: `cd "${CLAUDE_PLUGIN_ROOT}" && PYTHONPATH=packages/core:packages/connectors:packages/agents python3 -m apps.cli.main status`

### `/csm search <query>`
Search the registry for items matching the query.
Run: `cd "${CLAUDE_PLUGIN_ROOT}" && PYTHONPATH=packages/core:packages/connectors:packages/agents python3 -m apps.cli.main search "<query>"`

### `/csm inspect <item-id>`
Show detailed information about a specific item.
Run: `cd "${CLAUDE_PLUGIN_ROOT}" && PYTHONPATH=packages/core:packages/connectors:packages/agents python3 -m apps.cli.main inspect "<item-id>"`

### `/csm compare <item-a> <item-b>`
Compare two items side by side.
Run: `cd "${CLAUDE_PLUGIN_ROOT}" && PYTHONPATH=packages/core:packages/connectors:packages/agents python3 -m apps.cli.main compare "<item-a>" "<item-b>"`

### `/csm suggest`
Show recommendations based on current stack analysis. Run evaluate + propose:
Run: `cd "${CLAUDE_PLUGIN_ROOT}" && PYTHONPATH=packages/core:packages/connectors:packages/agents python3 -m apps.cli.main propose`

### `/csm propose`
Generate proposals for all evaluated candidates.
Run: `cd "${CLAUDE_PLUGIN_ROOT}" && PYTHONPATH=packages/core:packages/connectors:packages/agents python3 -m apps.cli.main propose`

### `/csm apply <proposal-id>`
Apply a pending proposal. Creates a snapshot first.
Run: `cd "${CLAUDE_PLUGIN_ROOT}" && PYTHONPATH=packages/core:packages/connectors:packages/agents python3 -m apps.cli.main apply "<proposal-id>"`
If the proposal involves a divan package, also run the appropriate `divan add/remove` command.

### `/csm scout`
Run a scouting pass across all enabled sources.
Run: `cd "${CLAUDE_PLUGIN_ROOT}" && PYTHONPATH=packages/core:packages/connectors:packages/agents python3 -m apps.cli.main scout`

### `/csm snapshot [description]`
Create a manual registry snapshot.
Run: `cd "${CLAUDE_PLUGIN_ROOT}" && PYTHONPATH=packages/core:packages/connectors:packages/agents python3 -m apps.cli.main snapshot`

### `/csm rollback <snapshot-id>`
Rollback the registry to a previous snapshot.
Run: `cd "${CLAUDE_PLUGIN_ROOT}" && PYTHONPATH=packages/core:packages/connectors:packages/agents python3 -m apps.cli.main rollback "<snapshot-id>"`

### `/csm build <description>`
Request the CSM builder to create a new skill/plugin/agent. Dispatch the csm-builder agent with the description.

### `/csm stop`
Stop the daemon loop (if running). Write `stop_requested: true` to the state file.

### `/csm serve`
Start the web UI and API server.
Run: `cd "${CLAUDE_PLUGIN_ROOT}" && PYTHONPATH=packages/core:packages/connectors:packages/agents python3 -m apps.cli.main serve`

If no action is recognized, show this help.
