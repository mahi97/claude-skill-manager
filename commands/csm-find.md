---
description: "Find a skill, plugin, or MCP server — searches registry and web if needed"
argument-hint: "<what you're looking for>"
---

# CSM Find

A high-level find command that combines registry search with web research.

Given the user's description in `$ARGUMENTS`:

1. **Search the local registry first**:
   ```bash
   cd "${CLAUDE_PLUGIN_ROOT}" && PYTHONPATH=packages/core:packages/connectors:packages/agents python3 -m apps.cli.main search "$ARGUMENTS"
   ```

2. **If good matches found**: Present them with trust/risk info and ask if the user wants to install.

3. **If no matches or poor matches**: Dispatch the `csm-researcher` agent to do a deep web search for what the user needs.

4. **If nothing exists anywhere**: Ask the user if they want CSM to build it. If yes, dispatch the `csm-builder` agent.

Always present results in a clear table format with:
- Name, type, source
- Trust tier and risk score
- Whether it's already installed, a candidate, or newly discovered
- Your recommendation
