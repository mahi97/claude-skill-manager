# Security Model

## Core Principle

CSM is safe by default. It discovers and evaluates but never auto-installs or auto-executes third-party code.

## Trust Model

### Trust Tiers

Every source and discovered item is assigned a trust tier:

| Tier | Meaning | Auto-actions allowed |
|------|---------|---------------------|
| **official** | From Anthropic or verified first-party | Evaluation, proposal generation |
| **curated** | Reviewed by trusted maintainers | Evaluation, proposal generation |
| **community** | Community-sourced, not formally reviewed | Evaluation, proposal generation |
| **untrusted** | Unknown provenance | Evaluation only, flagged |

No tier permits auto-installation. All tiers require explicit user approval to apply changes.

### Trust Inheritance

Items inherit the trust tier of their source by default. Users can override trust tiers on individual items.

## Risk Assessment

### Risk Flags

Each item is assessed for these risk signals:

| Flag | Why it matters |
|------|---------------|
| **shell_execution** | Can run arbitrary commands on your machine |
| **network_calls** | Can exfiltrate data or fetch remote code |
| **external_mcp_access** | Can interact with external services via MCP |
| **wide_filesystem_access** | Can read/write outside its expected scope |
| **opaque_install_method** | Install process is not inspectable |
| **low_repo_activity** | Source may be abandoned or unmaintained |
| **missing_docs** | Hard to verify what the item does |
| **missing_license** | Legal risk; unclear usage terms |

### Risk Score

A normalized 0-1 score derived from the number and severity of risk flags. Used in evaluation weighting and displayed in proposals and UI.

## Policy Rules

Policies in `registry/policies.yaml` define automated constraints:

- **No Auto-Install**: All installations require explicit approval
- **Block Untrusted Shell**: Items with `untrusted` trust and `shell_execution` risk cannot be auto-approved
- **Require License**: Items without a license are flagged for review
- **Snapshot Before Apply**: Every apply creates a snapshot first
- **Max Risk Threshold**: Items with risk > 0.7 require explicit override

## What CSM Does NOT Do

1. **Execute third-party code**: CSM reads metadata and files but never runs install scripts or third-party executables.
2. **Modify Claude Code configuration**: CSM updates its own registry files. It does not modify `.claude/settings.json`, `.mcp.json`, or other Claude Code config files.
3. **Send data externally**: Scout operations fetch public metadata. CSM does not upload your registry, installed items, or usage data anywhere.
4. **Auto-approve anything**: Every change goes through the proposal pipeline and requires explicit user action to apply.

## Threat Model

### Threats Addressed

- **Supply chain attacks**: Trust tiers and risk flags surface suspicious items before they reach your stack.
- **Configuration drift**: The proposal-driven model prevents untracked changes.
- **Accidental breakage**: Snapshots before every mutation enable instant rollback.
- **Social engineering**: Risk flags for opaque install methods and missing docs help identify suspicious items.

### Threats NOT Addressed (Future Work)

- **Signature verification**: CSM does not verify cryptographic signatures on items.
- **Sandboxed evaluation**: CSM does not run items in a sandbox to observe behavior.
- **Dependency graph attacks**: Transitive dependency analysis is not implemented yet.
- **Compromised sources**: If a trusted source is compromised, CSM trusts it until the user changes the trust tier.

## Recommendations

1. Set `GITHUB_TOKEN` to a read-only token with minimal permissions.
2. Review proposals before applying, especially for community/untrusted items.
3. Keep snapshots around — they're small and enable easy rollback.
4. Periodically review your sources and their trust tiers.
5. Don't add untrusted sources with auto-enabled scouting unless you review candidates regularly.
