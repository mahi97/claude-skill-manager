"""Deterministic evaluator for candidate items. Pluggable for future Claude-based evaluation."""

from __future__ import annotations

from datetime import datetime, timezone

from .models import (
    EvaluationReport,
    EvaluationScore,
    ItemStatus,
    RegistryItem,
    RiskAssessment,
    RiskFlag,
    TrustTier,
)


def evaluate_freshness(item: RegistryItem) -> EvaluationScore:
    """Score based on how recently the item was updated/seen."""
    if item.last_seen_at:
        last_seen = item.last_seen_at if item.last_seen_at.tzinfo else item.last_seen_at.replace(tzinfo=timezone.utc)
        days_old = (datetime.now(timezone.utc) - last_seen).days
        if days_old < 7:
            score = 1.0
        elif days_old < 30:
            score = 0.8
        elif days_old < 90:
            score = 0.5
        elif days_old < 365:
            score = 0.3
        else:
            score = 0.1
    else:
        score = 0.2  # Unknown freshness
    return EvaluationScore(dimension="freshness", score=score, weight=1.0, reasoning=f"Last seen: {item.last_seen_at}")


def evaluate_documentation(item: RegistryItem) -> EvaluationScore:
    """Score based on documentation signals."""
    has_desc = len(item.description) > 20
    has_missing_docs = RiskFlag.MISSING_DOCS in item.risk.flags
    if has_desc and not has_missing_docs:
        score = 0.8
    elif has_desc:
        score = 0.5
    else:
        score = 0.2
    return EvaluationScore(
        dimension="documentation", score=score, weight=0.8, reasoning=f"Description length: {len(item.description)}"
    )


def evaluate_trust(item: RegistryItem) -> EvaluationScore:
    """Score based on trust tier."""
    tier_scores = {
        TrustTier.OFFICIAL: 1.0,
        TrustTier.CURATED: 0.8,
        TrustTier.COMMUNITY: 0.5,
        TrustTier.UNTRUSTED: 0.1,
    }
    score = tier_scores.get(item.trust_tier, 0.1)
    return EvaluationScore(dimension="trust", score=score, weight=1.2, reasoning=f"Trust tier: {item.trust_tier.value}")


def evaluate_risk(item: RegistryItem) -> EvaluationScore:
    """Score inversely based on risk flags."""
    n_flags = len(item.risk.flags)
    if n_flags == 0:
        score = 1.0
    elif n_flags <= 2:
        score = 0.6
    elif n_flags <= 4:
        score = 0.3
    else:
        score = 0.1
    return EvaluationScore(dimension="risk", score=score, weight=1.5, reasoning=f"Risk flags: {n_flags}")


def evaluate_overlap(item: RegistryItem, installed: list[RegistryItem]) -> EvaluationScore:
    """Score based on overlap with installed items."""
    overlap_ids = []
    for inst in installed:
        if inst.type == item.type and set(inst.categories) & set(item.categories):
            overlap_ids.append(inst.id)
    if not overlap_ids:
        score = 1.0
        reasoning = "No overlap with installed items"
    elif len(overlap_ids) == 1:
        score = 0.6
        reasoning = f"Overlaps with: {overlap_ids[0]}"
    else:
        score = 0.3
        reasoning = f"Overlaps with: {', '.join(overlap_ids)}"
    return EvaluationScore(dimension="overlap", score=score, weight=0.8, reasoning=reasoning)


def evaluate_item(item: RegistryItem, installed: list[RegistryItem] | None = None) -> EvaluationReport:
    """Run full deterministic evaluation on a candidate item."""
    installed = installed or []
    scores = [
        evaluate_freshness(item),
        evaluate_documentation(item),
        evaluate_trust(item),
        evaluate_risk(item),
        evaluate_overlap(item, installed),
    ]

    total_weight = sum(s.weight for s in scores)
    weighted_sum = sum(s.score * s.weight for s in scores)
    overall = weighted_sum / total_weight if total_weight > 0 else 0.0

    overlap_ids = []
    for inst in installed:
        if inst.type == item.type and set(inst.categories) & set(item.categories):
            overlap_ids.append(inst.id)

    if overall >= 0.7:
        recommendation = "Recommend install"
    elif overall >= 0.4:
        recommendation = "Review manually"
    else:
        recommendation = "Not recommended"

    return EvaluationReport(
        id=f"eval-{item.id}",
        item_id=item.id,
        scores=scores,
        overall_score=round(overall, 3),
        recommendation=recommendation,
        overlap_with=overlap_ids,
        risk_assessment=item.risk,
        evaluator="deterministic-v1",
    )
