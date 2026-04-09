"""Tests for proposal generation."""

from csm_core.evaluator import evaluate_item
from csm_core.models import (
    Category,
    ItemType,
    ProposalAction,
    RegistryItem,
    RiskAssessment,
    TrustTier,
)
from csm_core.proposer import generate_proposal


def _make_item(**overrides) -> RegistryItem:
    defaults = {
        "id": "test-item",
        "name": "test",
        "type": ItemType.SKILL,
        "description": "A test skill for proposal testing",
        "categories": [Category.CODING],
        "trust_tier": TrustTier.CURATED,
        "risk": RiskAssessment(flags=[], score=0.1),
    }
    defaults.update(overrides)
    return RegistryItem(**defaults)


def test_generate_install_proposal():
    item = _make_item()
    report = evaluate_item(item)
    proposal = generate_proposal(item, report, installed=[])

    assert proposal.title
    assert proposal.summary
    assert len(proposal.changes) == 1
    assert proposal.changes[0].action == ProposalAction.INSTALL


def test_generate_reject_proposal():
    item = _make_item(
        trust_tier=TrustTier.UNTRUSTED,
        description="",
        risk=RiskAssessment(
            flags=["shell_execution", "network_calls", "missing_docs", "missing_license", "opaque_install_method"],
            score=0.9,
        ),
    )
    report = evaluate_item(item)
    if report.recommendation == "Not recommended":
        proposal = generate_proposal(item, report, installed=[])
        assert proposal.changes[0].action == ProposalAction.REJECT


def test_proposal_has_risk_summary():
    item = _make_item()
    report = evaluate_item(item)
    proposal = generate_proposal(item, report, installed=[])
    assert proposal.risk_summary
    assert proposal.trust_summary


def test_proposal_has_overlap_analysis():
    item = _make_item(categories=[Category.CODING])
    installed = [_make_item(id="existing", name="existing")]
    report = evaluate_item(item, installed)
    proposal = generate_proposal(item, report, installed)
    assert proposal.overlap_analysis
