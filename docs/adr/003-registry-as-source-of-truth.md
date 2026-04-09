# ADR 003: Registry as Source of Truth

## Status

Accepted

## Context

We need a canonical data store for the state of the user's Claude Code ecosystem. Options include a database, configuration files, or a structured file-based registry.

## Decision

The `registry/` directory of YAML files is the single source of truth:

- `installed.yaml` — what's in the active stack
- `candidates.yaml` — what's been discovered but not acted on
- `rejected.yaml` — what's been explicitly rejected
- `sources.yaml` — where to look for new items
- `policies.yaml` — automation constraints
- `taxonomy.yaml` — category definitions
- `proposals/` — change proposals (one YAML file per proposal)
- `evaluations/` — evaluation reports (one YAML file per evaluation)

## Consequences

**Positive:**
- Human-readable and editable
- Git-friendly (diffable, mergeable, branchable)
- No database setup or migration
- Easy to inspect the full state at any time
- Snapshots are just directory copies
- Portable between machines

**Negative:**
- No query optimization (full file scan for searches)
- No transactions or concurrent write safety
- File I/O on every operation (acceptable for personal-scale data)
- YAML parsing is slower than database reads

## Performance Notes

For a personal registry of hundreds of items, YAML I/O takes single-digit milliseconds. Performance concerns only arise at thousands of items, at which point adding a SQLite index layer would be straightforward without changing the YAML source of truth.

## Alternatives Considered

- **SQLite**: Better performance and querying, but less human-readable and harder to diff in git. Good candidate for a future caching layer.
- **JSON**: Slightly faster parsing but less readable for complex nested structures. YAML's comment support and multi-line strings are valuable for the registry.
- **TOML**: Good for config but awkward for arrays of complex objects.
