# ADR 001: Local-First Architecture

## Status

Accepted

## Context

CSM manages the user's Claude Code ecosystem — skills, plugins, hooks, MCP servers. This is sensitive configuration that directly affects how their AI assistant behaves. We need to decide where state lives and how the system operates.

## Decision

CSM is local-first:

1. All state lives in local YAML files (the registry)
2. No cloud database, no remote API for core operations
3. No account, no login, no remote auth
4. Network access is only used for scouting (fetching metadata from configured sources)
5. The system works fully offline with local sources

## Consequences

**Positive:**
- User has full control and visibility over their data
- No vendor lock-in or service dependency
- Works offline
- Easy to version control (git)
- Easy to inspect, debug, and manually edit
- No security concerns about remote data storage

**Negative:**
- No multi-machine sync out of the box (future: export/import or git-based sync)
- No collaborative features
- No hosted dashboard (must run locally)
- Scale limited to what fits in YAML files (sufficient for personal use)

## Alternatives Considered

- **SQLite database**: More structured but less human-readable and harder to diff in git. May be added as a cache/index layer later.
- **Cloud-hosted registry**: Better for teams but adds complexity, auth, and trust requirements that conflict with the security model.
