"""Shared test fixtures."""

import shutil
import sys
from pathlib import Path

import pytest

# Add package paths
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "packages" / "core"))
sys.path.insert(0, str(ROOT / "packages" / "connectors"))
sys.path.insert(0, str(ROOT / "packages" / "agents"))

from csm_core.registry import Registry, SnapshotManager


@pytest.fixture
def tmp_registry(tmp_path):
    """Create a temporary registry with seed data."""
    reg_dir = tmp_path / "registry"
    reg_dir.mkdir()
    (reg_dir / "proposals").mkdir()
    (reg_dir / "evaluations").mkdir()

    # Copy seed data
    seed_dir = ROOT / "registry"
    for f in ["installed.yaml", "candidates.yaml", "rejected.yaml", "sources.yaml", "policies.yaml", "taxonomy.yaml"]:
        src = seed_dir / f
        if src.exists():
            shutil.copy2(src, reg_dir / f)

    return Registry(reg_dir)


@pytest.fixture
def tmp_snapshot_mgr(tmp_path, tmp_registry):
    """Create a snapshot manager with temp dirs."""
    snap_dir = tmp_path / "snapshots"
    snap_dir.mkdir()
    return SnapshotManager(tmp_registry.base_dir, snap_dir)
