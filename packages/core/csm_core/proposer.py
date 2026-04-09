"""Proposal generation from evaluation reports."""

from __future__ import annotations

from datetime import datetime, timezone

from .models import (
    EvaluationReport,
    Proposal,
    ProposalAction,
    ProposalChange,
    RegistryItem,
)


def _determine_action(report: EvaluationReport, item: RegistryItem, installed: list[RegistryItem]) -> ProposalAction:
    """Determine proposal action based on evaluation."""
    if report.recommendation == "Not recommended":
        return ProposalAction.REJECT

    # Check if this would replace an existing item
    for inst in installed:
        if inst.type == item.type and inst.name == item.name:
            return ProposalAction.UPGRADE
        for rel in item.relationships:
            if rel.type.value == "supersedes" and rel.target_id == inst.id:
                return ProposalAction.REPLACE

    return ProposalAction.INSTALL


def generate_proposal(
    item: RegistryItem,
    report: EvaluationReport,
    installed: list[RegistryItem],
) -> Proposal:
    """Generate a structured proposal from an evaluated candidate."""
    action = _determine_action(report, item, installed)

    change = ProposalChange(
        action=action,
        item_id=item.id,
        item_name=item.name,
        description=f"{action.value.title()} {item.type.value}: {item.name}",
        registry_diff={
            "add_to": "installed" if action in (ProposalAction.INSTALL, ProposalAction.UPGRADE, ProposalAction.REPLACE) else "rejected",
            "item": item.model_dump(mode="json"),
        },
    )

    overlap_text = ""
    if report.overlap_with:
        overlap_text = f"Overlaps with existing items: {', '.join(report.overlap_with)}. "
        if action == ProposalAction.REPLACE:
            overlap_text += "This item is proposed as a replacement."
        else:
            overlap_text += "Consider whether both are needed."

    risk_lines = []
    if item.risk.flags:
        risk_lines = [f"- {f.value}" for f in item.risk.flags]
    risk_text = "\n".join(risk_lines) if risk_lines else "No risk flags detected."

    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

    return Proposal(
        id=f"proposal-{item.id}-{ts}",
        title=f"{action.value.title()} {item.type.value} '{item.name}'",
        summary=f"Proposal to {action.value} {item.type.value} '{item.name}' from source {item.source_url or 'unknown'}.",
        changes=[change],
        why_it_matters=item.description or "No description provided.",
        overlap_analysis=overlap_text or "No overlap with current stack.",
        trust_summary=f"Trust tier: {item.trust_tier.value}. Source: {item.source_url or 'unknown'}.",
        risk_summary=risk_text,
        workflow_impact=f"Adds a new {item.type.value} to the Claude Code stack." if action == ProposalAction.INSTALL else f"{action.value.title()}s {item.type.value} in the stack.",
        recommendation=report.recommendation,
    )


def generate_proposals_batch(
    candidates: list[RegistryItem],
    reports: dict[str, EvaluationReport],
    installed: list[RegistryItem],
) -> list[Proposal]:
    """Generate proposals for a batch of evaluated candidates."""
    proposals = []
    for item in candidates:
        report = reports.get(item.id)
        if report:
            proposals.append(generate_proposal(item, report, installed))
    return proposals
