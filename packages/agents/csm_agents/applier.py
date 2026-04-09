"""Apply agent - applies approved proposals with safety checks."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from csm_core.models import ProposalAction, ProposalStatus
from csm_core.registry import Registry, SnapshotManager

logger = logging.getLogger(__name__)


class ApplyAgent:
    """Applies approved proposals to the registry with snapshot safety."""

    def __init__(self, registry: Registry, snapshot_mgr: SnapshotManager | None = None):
        self.registry = registry
        self.snapshot_mgr = snapshot_mgr or SnapshotManager(registry.base_dir)

    def apply_proposal(self, proposal_id: str) -> dict:
        """Apply a proposal by ID. Creates a snapshot first."""
        proposals = self.registry.load_proposals()
        proposal = next((p for p in proposals if p.id == proposal_id), None)

        if not proposal:
            return {"success": False, "error": f"Proposal not found: {proposal_id}"}

        if proposal.status != ProposalStatus.PENDING:
            return {"success": False, "error": f"Proposal is {proposal.status.value}, not pending"}

        # Create pre-apply snapshot
        logger.info(f"Creating snapshot before applying {proposal_id}")
        snapshot = self.snapshot_mgr.create_snapshot(
            description=f"Before applying {proposal.title}",
            trigger=f"pre-apply:{proposal_id}",
        )

        # Apply each change
        applied = []
        errors = []
        for change in proposal.changes:
            try:
                if change.action in (ProposalAction.INSTALL, ProposalAction.UPGRADE, ProposalAction.REPLACE):
                    ok = self.registry.install_item(change.item_id)
                    if ok:
                        applied.append(change.item_id)
                        logger.info(f"  Installed: {change.item_name}")
                    else:
                        errors.append(f"Could not install {change.item_id}")

                elif change.action == ProposalAction.REJECT:
                    ok = self.registry.reject_item(change.item_id, reason=change.description)
                    if ok:
                        applied.append(change.item_id)
                        logger.info(f"  Rejected: {change.item_name}")
                    else:
                        errors.append(f"Could not reject {change.item_id}")

                elif change.action == ProposalAction.REMOVE:
                    # Remove from installed (move back to rejected)
                    installed = self.registry.load_installed()
                    target = None
                    remaining = []
                    for item in installed:
                        if item.id == change.item_id:
                            target = item
                        else:
                            remaining.append(item)
                    if target:
                        self.registry.save_installed(remaining)
                        target.status = "rejected"
                        rejected = self.registry.load_rejected()
                        rejected.append(target)
                        self.registry.save_rejected(rejected)
                        applied.append(change.item_id)
                        logger.info(f"  Removed: {change.item_name}")
                    else:
                        errors.append(f"Item not found in installed: {change.item_id}")

            except Exception as e:
                errors.append(f"Error applying {change.item_id}: {e}")

        # Update proposal status
        proposal.status = ProposalStatus.APPLIED if not errors else ProposalStatus.PENDING
        proposal.applied_at = datetime.now(timezone.utc)
        proposal.snapshot_id = snapshot.id
        self.registry.save_proposal(proposal)

        return {
            "success": len(errors) == 0,
            "applied": applied,
            "errors": errors,
            "snapshot_id": snapshot.id,
        }
