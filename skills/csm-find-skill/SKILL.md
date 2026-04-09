---
name: csm-find-skill
description: "Use when the user asks to find, search for, discover, or locate a Claude Code skill, plugin, MCP server, hook, or subagent. Triggers on: 'find me a plugin', 'is there a skill for', 'search for MCP server', 'I need a tool that', 'what plugins exist for', 'look for a skill'."
---

# CSM Find — Skill/Plugin Discovery

The user is looking for a Claude Code ecosystem component. Use CSM to find it.

## Step 1: Search the local registry

```bash
cd "${CLAUDE_PLUGIN_ROOT}" && PYTHONPATH=packages/core:packages/connectors:packages/agents python3 -m apps.cli.main search "<user's query>"
```

## Step 2: Present results

If matches found, show them with:
- Name, type, status (installed/candidate/rejected)
- Trust tier and risk score
- Brief description
- Whether it's already in their stack

## Step 3: If no good matches

Tell the user you'll research it. Dispatch the `csm-researcher` agent:

```
Agent({
  subagent_type: "csm-researcher",
  prompt: "Research Claude Code ecosystem for: <user's need>. Search GitHub, npm, community resources. Report findings as candidate items."
})
```

## Step 4: If nothing exists

Offer to build it:
"I couldn't find an existing component for that. Want me to build one? I can create a skill/plugin/agent that does what you need."

If they say yes, dispatch `csm-builder`.

## Step 5: If user wants to install

For divan-managed packages: "I'll need your approval to add this via divan."
For CSM-internal additions: proceed with more autonomy.
