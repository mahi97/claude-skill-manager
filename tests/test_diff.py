"""Tests for diff generation."""

from csm_core.diff import diff_items, diff_registry_state
from csm_core.models import Category, ItemType, RegistryItem, TrustTier


def _make_item(**overrides) -> RegistryItem:
    defaults = {
        "id": "test-item",
        "name": "test",
        "type": ItemType.SKILL,
        "categories": [Category.CODING],
        "trust_tier": TrustTier.COMMUNITY,
    }
    defaults.update(overrides)
    return RegistryItem(**defaults)


def test_diff_identical_items():
    a = _make_item()
    b = _make_item()
    d = diff_items(a, b)
    assert len(d["changes"]) == 0
    assert "identical" in d["summary"].lower()


def test_diff_different_items():
    a = _make_item(name="alpha", trust_tier=TrustTier.COMMUNITY)
    b = _make_item(id="test-item-b", name="beta", trust_tier=TrustTier.OFFICIAL)
    d = diff_items(a, b)
    assert len(d["changes"]) > 0
    assert "name" in d["changes"]


def test_diff_registry_state():
    before = [_make_item(id="a", name="A"), _make_item(id="b", name="B")]
    after = [_make_item(id="b", name="B"), _make_item(id="c", name="C")]
    d = diff_registry_state(before, after)
    assert "c" in d["added"]
    assert "a" in d["removed"]
