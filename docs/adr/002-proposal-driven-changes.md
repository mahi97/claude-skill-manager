# ADR 002: Proposal-Driven Changes

## Status

Accepted

## Context

CSM discovers third-party components from various sources with varying trust levels. We need a change model that is safe, auditable, and user-controlled.

## Decision

All registry mutations go through the proposal pipeline:

1. **Scout** discovers candidates
2. **Evaluate** scores them deterministically
3. **Propose** generates structured change proposals
4. **User reviews** the proposal (CLI, API, or web UI)
5. **Apply** executes the proposal with a pre-mutation snapshot

No component is installed, removed, or modified without an explicit proposal and user approval.

## Consequences

**Positive:**
- Full audit trail of every change
- User reviews trust, risk, and overlap before committing
- Rollback is always possible via snapshots
- Proposals serve as documentation of decisions
- Safe for experimentation — candidates don't affect the active stack

**Negative:**
- More friction for simple "just install it" cases
- Proposals accumulate if not reviewed regularly
- Multi-step workflow may feel heavy for power users

## Mitigations

- CLI provides direct `apply` for quick approval
- Future: policy rules could auto-approve items meeting specific criteria (e.g., official tier, zero risk flags)
- Proposal generation is idempotent — re-running doesn't create duplicates for already-evaluated items
