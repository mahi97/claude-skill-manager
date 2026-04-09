"""Tests for the deterministic evaluator."""

from datetime import datetime, timedelta, timezone

from csm_core.evaluator import evaluate_item
from csm_core.models import (
    Category,
    ItemType,
    RegistryItem,
    RiskAssessment,
    RiskFlag,
    TrustTier,
)


def _make_item(**overrides) -> RegistryItem:
    defaults = {
        "id": "test-item",
        "name": "test",
        "type": ItemType.SKILL,
        "description": "A test item for evaluation testing",
        "categories": [Category.CODING],
        "trust_tier": TrustTier.COMMUNITY,
        "risk": RiskAssessment(flags=[], score=0.0),
        "last_seen_at": datetime.now(timezone.utc) - timedelta(days=5),
    }
    defaults.update(overrides)
    return RegistryItem(**defaults)


def test_evaluate_high_quality_item():
    item = _make_item(
        trust_tier=TrustTier.OFFICIAL,
        description="A well-documented official skill with clear purpose",
        last_seen_at=datetime.now(timezone.utc) - timedelta(days=1),
    )
    report = evaluate_item(item)
    assert report.overall_score > 0.7
    assert report.recommendation == "Recommend install"


def test_evaluate_low_quality_item():
    item = _make_item(
        trust_tier=TrustTier.UNTRUSTED,
        description="",
        risk=RiskAssessment(
            flags=[RiskFlag.SHELL_EXECUTION, RiskFlag.NETWORK_CALLS, RiskFlag.MISSING_DOCS, RiskFlag.MISSING_LICENSE, RiskFlag.OPAQUE_INSTALL_METHOD],
            score=0.8,
        ),
        last_seen_at=datetime.now(timezone.utc) - timedelta(days=400),
    )
    report = evaluate_item(item)
    assert report.overall_score < 0.4
    assert report.recommendation == "Not recommended"


def test_evaluate_with_overlap():
    item = _make_item(categories=[Category.CODING])
    installed = [
        _make_item(id="existing", name="existing", categories=[Category.CODING]),
    ]
    report = evaluate_item(item, installed)
    assert len(report.overlap_with) > 0


def test_evaluate_no_overlap():
    item = _make_item(categories=[Category.SCIENTIFIC])
    installed = [
        _make_item(id="existing", name="existing", categories=[Category.DEVOPS]),
    ]
    report = evaluate_item(item, installed)
    assert len(report.overlap_with) == 0


def test_evaluate_produces_all_dimensions():
    item = _make_item()
    report = evaluate_item(item)
    dimensions = {s.dimension for s in report.scores}
    assert "freshness" in dimensions
    assert "documentation" in dimensions
    assert "trust" in dimensions
    assert "risk" in dimensions
    assert "overlap" in dimensions
