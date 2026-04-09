# CLAUDE.md

This is **Claude Skill Manager (CSM)** — a divan plugin that acts as a persistent operating layer for the Claude Code ecosystem.

## What This Is

CSM is a divan-installed plugin that:
- Runs as a persistent daemon in a dedicated tmux session
- Continuously scouts for new skills, plugins, MCP servers, and related components
- Evaluates discoveries against the installed stack
- Proposes changes through structured reports (never silently installs)
- Can create new skills/agents/workflows when nothing suitable exists
- Provides /csm slash commands and a `csm` CLI

## Project Structure

This is both a **divan plugin** (`.claude-plugin/`, `skills/`, `agents/`, `commands/`, `hooks/`) and a **Python application** (`packages/`, `apps/`).

```
.claude-plugin/       Plugin manifest for divan
skills/               Natural language activated skills (SKILL.md)
agents/               Subagent team (daemon, scout, evaluator, proposer, builder, researcher)
commands/             Slash commands (/csm, /csm-daemon, /csm-find, /csm-stop)
hooks/                Stop hook for daemon persistence + scripts
packages/core/        Python domain models, registry, evaluator, proposer, graph, diff
packages/connectors/  Source connectors (GitHub, marketplace, local)
packages/agents/      Python agent modules (scout, pipeline, applier)
apps/api/             FastAPI REST backend
apps/cli/             Typer CLI
apps/web/             React + Vite dashboard
registry/             Canonical YAML registry (source of truth)
scripts/              csm CLI wrapper, start-daemon.sh
```

## Key Commands

```bash
# From any terminal (via scripts/csm wrapper)
csm status                    # Registry overview
csm search <query>            # Search registry
csm scout                     # Scout sources
csm propose                   # Generate proposals
csm daemon                    # Start daemon in tmux
csm attach                    # Attach to daemon

# From inside Claude Code (slash commands)
/csm status                   # Same commands via slash
/csm search <query>
/csm-find <description>       # Deep search + web research
/csm-daemon                   # Start persistent loop
```

## Python Engine

All Python commands need the PYTHONPATH set:
```bash
PYTHONPATH=packages/core:packages/connectors:packages/agents python3 -m apps.cli.main <command>
```

## Autonomy Model

- **CSM's own packages**: High autonomy locally, PRs for major changes
- **Divan packages**: Requires user approval, managed via `divan add/remove`

## Divan Profile: full

```bash
divan status       # Show what's installed
divan add <plugin> # Add a plugin
divan remove <p>   # Remove a plugin
divan sync         # Re-sync from profile
divan list         # Browse the full collection
```
