# Claude Skill Manager (CSM)

A persistent, local-first operating layer for the Claude Code ecosystem. Installed as a [divan](https://github.com/mahi97/divan) plugin, CSM runs as an always-on background daemon that scouts, evaluates, and proposes changes to your skill/plugin stack — and can build new components when nothing suitable exists.

## How It Works

```
┌─────────────────────────────────────────────────────────┐
│                    tmux: csm-daemon                      │
│                                                          │
│  Claude Code + CSM daemon agent                          │
│  ├── Scouts sources continuously                         │
│  ├── Evaluates candidates against your stack             │
│  ├── Generates proposals (never silently installs)       │
│  ├── Responds to /csm commands from user                 │
│  └── Dispatches subagent team:                           │
│      ├── csm-scout      (source discovery)               │
│      ├── csm-evaluator  (deep comparison)                │
│      ├── csm-proposer   (proposal generation)            │
│      ├── csm-builder    (create new components)          │
│      └── csm-researcher (web research)                   │
└─────────────────────────────────────────────────────────┘
         ▲                              ▲
         │ /csm commands                │ csm CLI
         │ (inside tmux)                │ (any terminal)
         │                              │
    ┌────┴────┐                    ┌────┴────┐
    │ User in │                    │ User in │
    │  tmux   │                    │  shell  │
    └─────────┘                    └─────────┘
```

## Setup

### Prerequisites

- Python 3.12+ with [uv](https://docs.astral.sh/uv/)
- Node.js 20+ (for web UI)
- [divan](https://github.com/mahi97/divan) (plugin manager)
- tmux

### Install

```bash
# Install as a divan plugin (when published)
divan add claude-skill-manager

# Or for development, install dependencies directly:
cd claude-skill-manager
uv sync --all-extras
cd apps/web && npm install && cd ../..

# Add csm to PATH (optional)
ln -s $(pwd)/scripts/csm ~/.local/bin/csm
```

## Usage

### Start the Daemon

```bash
# Launch persistent daemon in tmux
csm daemon
# or
./scripts/start-daemon.sh

# Attach to see what it's doing
csm attach
# or
tmux attach -t csm-daemon
```

### Interactive Commands (inside any Claude Code session)

```
/csm status              Show registry overview
/csm search <query>      Search for items
/csm inspect <item-id>   Detailed item view
/csm compare <a> <b>     Side-by-side comparison
/csm suggest             Get recommendations
/csm propose             Generate proposals
/csm apply <proposal-id> Apply with snapshot safety
/csm scout               Run a scouting pass
/csm-find <what>         Deep search + web research + offer to build
/csm-stop                Stop the daemon
```

### CLI (from any terminal)

```bash
csm status               # Registry overview
csm search memory        # Search
csm scout                # Scout sources
csm propose              # Generate proposals
csm serve                # Start API + web UI
csm divan add <plugin>   # Add via divan
csm find "slack tool"    # Queue research request to daemon
csm build "arxiv reader" # Queue build request to daemon
```

### Web Dashboard

```bash
csm serve   # API on :8000, docs at /docs
csm web     # Web UI on :5173
```

Dashboard shows: installed stack, candidates, proposals, source status, graph visualization, snapshots.

## Architecture

### Divan Plugin Layer

```
.claude-plugin/plugin.json    Plugin manifest
skills/                       Natural language triggers
  csm-find-skill/             "find me a plugin for..."
  csm-manage-stack/           "install/remove/upgrade..."
  csm-ecosystem-advisor/      "what should I install..."
agents/                       Subagent team
  csm-daemon.md               Main persistent agent
  csm-scout.md                Discovery agent
  csm-evaluator.md            Comparison/scoring agent
  csm-proposer.md             Proposal generation agent
  csm-builder.md              Component creation agent
  csm-researcher.md           Web research agent
commands/                     Slash commands
  csm.md                      /csm <action>
  csm-daemon.md               /csm-daemon
  csm-find.md                 /csm-find <query>
  csm-stop.md                 /csm-stop
hooks/
  hooks.json                  Stop hook (keeps daemon alive)
```

### Python Engine

```
packages/core/                Domain models, registry, evaluator, proposer
packages/connectors/          GitHub, marketplace, local directory connectors
packages/agents/              Scout, pipeline, apply orchestration
apps/api/                     FastAPI REST backend
apps/cli/                     Typer CLI
apps/web/                     React + Vite + Tailwind dashboard
```

### Registry (Source of Truth)

```
registry/
  installed.yaml              Your active stack
  candidates.yaml             Discovered items pending review
  rejected.yaml               Explicitly rejected items
  sources.yaml                Configured discovery sources
  policies.yaml               Automation policy rules
  taxonomy.yaml               Category definitions
  proposals/                  Change proposals
  evaluations/                Evaluation reports
```

## Autonomy Model

| Scope | Autonomy | Approval |
|-------|----------|----------|
| CSM's own skills/agents/workflows | High — can add/modify locally | Major changes via GitHub PR |
| Divan packages (user's stack) | Low — proposal only | Explicit user approval required |
| Registry data | Full — read/write freely | Snapshots for safety |
| External installs | None | Never auto-executes third-party code |

## Trust & Security

Every item is classified by trust tier (`official` / `curated` / `community` / `untrusted`) and risk flags (`shell_execution`, `network_calls`, `filesystem_access`, etc.). Nothing is installed without the user seeing the risk assessment first.

Snapshots are created before every mutation. Rollback is always one command away.

## Key Concepts

- **Proposal-driven**: Discover → Evaluate → Propose → User approves → Apply
- **Daemon loop**: Runs via Stop hook (like ralph-loop), iterates continuously
- **Request queue**: External sessions queue requests via files, daemon picks them up
- **Subagent team**: Daemon dispatches specialized agents for heavy work
- **Self-extending**: CSM can build new skills/plugins when nothing exists

## Development

```bash
uv sync --all-extras          # Install Python deps
cd apps/web && npm install    # Install web deps
just test                     # Run 30 tests
just lint                     # Ruff + format check
just api                      # Start API server
just web                      # Start web UI
```

## Current Limitations

- GitHub scouting requires `GITHUB_TOKEN` env var
- Marketplace connector is a placeholder (no official API yet)
- Evaluation is deterministic-only (Claude-powered evaluation is a pluggable future addition)
- No cryptographic signature verification on discovered items
- Single-user, local-only (no multi-machine sync yet)

## License

MIT
