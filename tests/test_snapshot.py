"""Tests for snapshot creation and rollback."""


def test_create_snapshot(tmp_snapshot_mgr):
    snap = tmp_snapshot_mgr.create_snapshot(description="Test snapshot", trigger="test")
    assert snap.id.startswith("snap-")
    assert len(snap.file_manifest) > 0


def test_list_snapshots(tmp_snapshot_mgr):
    tmp_snapshot_mgr.create_snapshot(description="Snap 1")
    tmp_snapshot_mgr.create_snapshot(description="Snap 2")
    snaps = tmp_snapshot_mgr.list_snapshots()
    assert len(snaps) >= 2


def test_rollback(tmp_registry, tmp_snapshot_mgr):
    # Create snapshot of current state
    snap = tmp_snapshot_mgr.create_snapshot(description="Before change")

    # Modify registry
    installed = tmp_registry.load_installed()
    original_count = len(installed)
    if installed:
        tmp_registry.save_installed(installed[1:])  # Remove first item
        assert len(tmp_registry.load_installed()) == original_count - 1

    # Rollback
    ok = tmp_snapshot_mgr.rollback(snap.id)
    assert ok is True

    # Should be restored
    restored = tmp_registry.load_installed()
    assert len(restored) == original_count


def test_rollback_nonexistent(tmp_snapshot_mgr):
    ok = tmp_snapshot_mgr.rollback("snap-does-not-exist")
    assert ok is False


def test_rollback_creates_backup(tmp_registry, tmp_snapshot_mgr):
    snap = tmp_snapshot_mgr.create_snapshot(description="Original")
    snaps_before = len(tmp_snapshot_mgr.list_snapshots())

    tmp_snapshot_mgr.rollback(snap.id)

    snaps_after = len(tmp_snapshot_mgr.list_snapshots())
    # Should have created a pre-rollback backup
    assert snaps_after > snaps_before
