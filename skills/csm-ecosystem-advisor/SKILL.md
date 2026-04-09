---
name: csm-ecosystem-advisor
description: "Use when the user asks for recommendations, suggestions, comparisons, or advice about their Claude Code setup. Triggers on: 'what should I install', 'suggest plugins', 'compare these plugins', 'what's good for', 'recommend a skill', 'what am I missing', 'analyze my stack', 'what can I improve'."
---

# CSM Ecosystem Advisor

The user wants advice about their Claude Code ecosystem. Provide informed recommendations based on the registry.

## For Suggestions/Recommendations

1. Load the current state:
   ```bash
   cd "${CLAUDE_PLUGIN_ROOT}" && PYTHONPATH=packages/core:packages/connectors:packages/agents python3 -m apps.cli.main status
   ```

2. Analyze gaps in their stack by category:
   - Check taxonomy coverage: which categories have installed items, which don't
   - Check for outdated items (low freshness scores)
   - Check for candidates with high evaluation scores

3. Present recommendations grouped by:
   - **Quick wins**: High-quality candidates ready to install
   - **Category gaps**: Categories with no installed items
   - **Upgrades available**: Items with newer versions
   - **Risk reduction**: Items that could replace riskier installed ones

## For Comparisons

```bash
cd "${CLAUDE_PLUGIN_ROOT}" && PYTHONPATH=packages/core:packages/connectors:packages/agents python3 -m apps.cli.main compare "<item-a>" "<item-b>"
```

Add qualitative analysis:
- Which has better documentation?
- Which has a more active community?
- Which fits the user's workflow better?
- Which has fewer risk flags?

## For Stack Analysis

Review the full installed stack and provide:
- Overall trust profile (how many official vs community items)
- Risk surface area (total risk flags across all items)
- Category coverage map
- Redundancy check (items that overlap significantly)
- Missing essentials (common useful plugins they don't have)
