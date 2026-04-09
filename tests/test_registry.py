"""Tests for registry load/save and query operations."""

from csm_core.models import Category, ItemStatus, ItemType, RegistryItem, RiskAssessment, TrustTier


def test_load_installed(tmp_registry):
    items = tmp_registry.load_installed()
    assert len(items) > 0
    assert all(isinstance(i, RegistryItem) for i in items)


def test_load_candidates(tmp_registry):
    items = tmp_registry.load_candidates()
    assert len(items) > 0


def test_load_sources(tmp_registry):
    sources = tmp_registry.load_sources()
    assert len(sources) > 0


def test_search_items(tmp_registry):
    results = tmp_registry.search_items("superpowers")
    assert len(results) > 0
    assert any("superpowers" in r.name for r in results)


def test_search_no_results(tmp_registry):
    results = tmp_registry.search_items("nonexistent_xyz_12345")
    assert len(results) == 0


def test_find_item(tmp_registry):
    item = tmp_registry.find_item("plugin-superpowers")
    assert item is not None
    assert item.name == "superpowers"


def test_find_item_not_found(tmp_registry):
    item = tmp_registry.find_item("does-not-exist")
    assert item is None


def test_add_candidate(tmp_registry):
    new_item = RegistryItem(
        id="test-new-item",
        name="test-item",
        type=ItemType.SKILL,
        description="A test item",
        categories=[Category.CODING],
        trust_tier=TrustTier.COMMUNITY,
        risk=RiskAssessment(flags=[], score=0.1),
    )
    added = tmp_registry.add_candidate(new_item)
    assert added is True

    # Should not add duplicate
    added2 = tmp_registry.add_candidate(new_item)
    assert added2 is False

    # Should be findable
    found = tmp_registry.find_item("test-new-item")
    assert found is not None
    assert found.status == ItemStatus.CANDIDATE


def test_add_candidate_already_installed(tmp_registry):
    """Should not add a candidate if it's already installed."""
    installed = tmp_registry.load_installed()
    if installed:
        dup = RegistryItem(
            id=installed[0].id,
            name="duplicate",
            type=ItemType.PLUGIN,
        )
        added = tmp_registry.add_candidate(dup)
        assert added is False


def test_install_item(tmp_registry):
    candidates_before = tmp_registry.load_candidates()
    assert len(candidates_before) > 0

    target_id = candidates_before[0].id
    ok = tmp_registry.install_item(target_id)
    assert ok is True

    # Should be in installed now
    installed = tmp_registry.load_installed()
    assert any(i.id == target_id for i in installed)

    # Should not be in candidates
    candidates_after = tmp_registry.load_candidates()
    assert not any(c.id == target_id for c in candidates_after)


def test_reject_item(tmp_registry):
    candidates = tmp_registry.load_candidates()
    assert len(candidates) > 0

    target_id = candidates[0].id
    ok = tmp_registry.reject_item(target_id, reason="Test rejection")
    assert ok is True

    rejected = tmp_registry.load_rejected()
    assert any(r.id == target_id for r in rejected)


def test_deduplicate_candidates(tmp_registry):
    # Add a duplicate manually
    candidates = tmp_registry.load_candidates()
    if candidates:
        candidates.append(candidates[0])
        tmp_registry.save_candidates(candidates)

        removed = tmp_registry.deduplicate_candidates()
        assert removed >= 1


def test_get_all_items(tmp_registry):
    all_items = tmp_registry.get_all_items()
    installed = tmp_registry.load_installed()
    candidates = tmp_registry.load_candidates()
    rejected = tmp_registry.load_rejected()
    assert len(all_items) == len(installed) + len(candidates) + len(rejected)
