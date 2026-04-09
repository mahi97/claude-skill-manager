---
name: csm-manage-stack
description: "Use when the user wants to install, remove, upgrade, update, or manage their Claude Code plugins and skills. Triggers on: 'install this plugin', 'remove that skill', 'upgrade my plugins', 'update my stack', 'what should I upgrade', 'clean up my plugins', 'add this to divan'."
---

# CSM Stack Management

The user wants to modify their Claude Code stack. CSM handles this through the proposal pipeline with divan integration.

## For Installing

1. Check if the item is in the registry:
   ```bash
   cd "${CLAUDE_PLUGIN_ROOT}" && PYTHONPATH=packages/core:packages/connectors:packages/agents python3 -m apps.cli.main inspect "<item-id>"
   ```

2. If it's a candidate, check its evaluation. If not evaluated, evaluate it:
   ```bash
   cd "${CLAUDE_PLUGIN_ROOT}" && PYTHONPATH=packages/core:packages/connectors:packages/agents python3 -m apps.cli.main evaluate
   ```

3. Show the user the trust/risk assessment and ask for confirmation.

4. If approved and it's a divan package:
   ```bash
   divan add <plugin-name>
   ```
   Then update the CSM registry to mark it as installed.

5. If it's a CSM-internal component (skill/agent/workflow you built), install it directly.

## For Removing

1. Show what depends on it (check relationships)
2. Get confirmation
3. For divan packages: `divan remove <plugin-name>`
4. Update registry

## For Upgrading

1. Check sources for newer versions
2. Compare old vs new (risk changes, breaking changes)
3. Present upgrade proposal
4. If approved: snapshot, then `divan sync` or reinstall

## Important

- ALWAYS snapshot before mutations: `/csm snapshot`
- ALWAYS show risk assessment before install
- NEVER silently modify the divan stack
- Log all changes to the registry
