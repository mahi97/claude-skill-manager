# Roadmap

## v0.1 (Current) — Foundation

- [x] Domain models and schemas
- [x] YAML registry with load/save/query
- [x] Source connectors (local, GitHub, marketplace)
- [x] Deterministic evaluator
- [x] Proposal generator
- [x] Snapshot and rollback
- [x] CLI with core commands
- [x] FastAPI backend
- [x] React web UI with dashboard, graph, proposals, sources, snapshots
- [x] Graph visualization with React Flow
- [x] Trust tiers and risk flags
- [x] Pre-seeded registry from real divan stack
- [x] Test suite

## v0.2 — Polish & Robustness

- [ ] Error handling and validation improvements
- [ ] CLI autocomplete and help text
- [ ] Web UI: search with filters
- [ ] Web UI: rich diff view for proposals
- [ ] Web UI: force-directed graph layout
- [ ] Policy engine enforcement (not just informational)
- [ ] Audit log for all mutations
- [ ] Better category inference in connectors
- [ ] Rate limiting for GitHub API calls
- [ ] Async scout with progress reporting

## v0.3 — Claude-Powered Evaluation

- [ ] Claude API integration for semantic evaluation
- [ ] Natural language overlap analysis
- [ ] Auto-generated proposal explanations
- [ ] Skill quality scoring (code review of skill content)
- [ ] Compatibility prediction

## v0.4 — Agent SDK Integration

- [ ] Refactor agents to Claude Agent SDK patterns
- [ ] Durable workflow for multi-step scouting
- [ ] Agent-driven proposal review
- [ ] Conversational proposal interface

## v0.5 — Ecosystem Expansion

- [ ] npm/PyPI connectors
- [ ] Hugging Face Hub connector
- [ ] Plugin dependency resolution
- [ ] Transitive dependency analysis
- [ ] Signature verification
- [ ] Export/import registries
- [ ] Multi-machine sync

## v1.0 — Production

- [ ] Comprehensive policy engine
- [ ] Sandboxed evaluation
- [ ] Full audit trail with git integration
- [ ] Scheduled scouting via GitHub Actions
- [ ] Dashboard analytics (trends, coverage)
- [ ] Plugin marketplace contribution workflow
