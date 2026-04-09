"""Registry operations - load, save, query, and mutate the canonical registry."""

from __future__ import annotations

import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from .models import (
    Category,
    EvaluationReport,
    ItemStatus,
    PolicyRule,
    Proposal,
    ProposalStatus,
    RegistryItem,
    Snapshot,
    Source,
    TaxonomyNode,
)

REGISTRY_DIR = Path("registry")


def _load_yaml(path: Path) -> Any:
    if not path.exists():
        return []
    with open(path) as f:
        data = yaml.safe_load(f)
    return data if data else []


def _save_yaml(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


class Registry:
    """Manages the canonical registry of Claude Code ecosystem components."""

    def __init__(self, base_dir: Path | None = None):
        self.base_dir = base_dir or REGISTRY_DIR
        self.installed_path = self.base_dir / "installed.yaml"
        self.candidates_path = self.base_dir / "candidates.yaml"
        self.rejected_path = self.base_dir / "rejected.yaml"
        self.sources_path = self.base_dir / "sources.yaml"
        self.policies_path = self.base_dir / "policies.yaml"
        self.taxonomy_path = self.base_dir / "taxonomy.yaml"
        self.proposals_dir = self.base_dir / "proposals"
        self.evaluations_dir = self.base_dir / "evaluations"

    # --- Load ---

    def load_items(self, path: Path) -> list[RegistryItem]:
        raw = _load_yaml(path)
        if not isinstance(raw, list):
            return []
        return [RegistryItem(**item) for item in raw]

    def load_installed(self) -> list[RegistryItem]:
        return self.load_items(self.installed_path)

    def load_candidates(self) -> list[RegistryItem]:
        return self.load_items(self.candidates_path)

    def load_rejected(self) -> list[RegistryItem]:
        return self.load_items(self.rejected_path)

    def load_sources(self) -> list[Source]:
        raw = _load_yaml(self.sources_path)
        if not isinstance(raw, list):
            return []
        return [Source(**s) for s in raw]

    def load_policies(self) -> list[PolicyRule]:
        raw = _load_yaml(self.policies_path)
        if not isinstance(raw, list):
            return []
        return [PolicyRule(**p) for p in raw]

    def load_taxonomy(self) -> list[TaxonomyNode]:
        raw = _load_yaml(self.taxonomy_path)
        if not isinstance(raw, list):
            return []
        return [TaxonomyNode(**t) for t in raw]

    def load_proposals(self) -> list[Proposal]:
        proposals = []
        if not self.proposals_dir.exists():
            return proposals
        for f in sorted(self.proposals_dir.glob("*.yaml")):
            raw = _load_yaml(f)
            if raw and isinstance(raw, dict):
                proposals.append(Proposal(**raw))
        return proposals

    def load_evaluations(self) -> list[EvaluationReport]:
        evals = []
        if not self.evaluations_dir.exists():
            return evals
        for f in sorted(self.evaluations_dir.glob("*.yaml")):
            raw = _load_yaml(f)
            if raw and isinstance(raw, dict):
                evals.append(EvaluationReport(**raw))
        return evals

    # --- Save ---

    def _items_to_dicts(self, items: list[RegistryItem]) -> list[dict]:
        return [item.model_dump(mode="json") for item in items]

    def save_installed(self, items: list[RegistryItem]) -> None:
        _save_yaml(self.installed_path, self._items_to_dicts(items))

    def save_candidates(self, items: list[RegistryItem]) -> None:
        _save_yaml(self.candidates_path, self._items_to_dicts(items))

    def save_rejected(self, items: list[RegistryItem]) -> None:
        _save_yaml(self.rejected_path, self._items_to_dicts(items))

    def save_sources(self, sources: list[Source]) -> None:
        _save_yaml(self.sources_path, [s.model_dump(mode="json") for s in sources])

    def save_proposal(self, proposal: Proposal) -> None:
        self.proposals_dir.mkdir(parents=True, exist_ok=True)
        path = self.proposals_dir / f"{proposal.id}.yaml"
        _save_yaml(path, proposal.model_dump(mode="json"))

    def save_evaluation(self, report: EvaluationReport) -> None:
        self.evaluations_dir.mkdir(parents=True, exist_ok=True)
        path = self.evaluations_dir / f"{report.id}.yaml"
        _save_yaml(path, report.model_dump(mode="json"))

    # --- Query ---

    def get_all_items(self) -> list[RegistryItem]:
        return self.load_installed() + self.load_candidates() + self.load_rejected()

    def find_item(self, item_id: str) -> RegistryItem | None:
        for item in self.get_all_items():
            if item.id == item_id:
                return item
        return None

    def search_items(self, query: str) -> list[RegistryItem]:
        query = query.lower()
        results = []
        for item in self.get_all_items():
            if (
                query in item.id.lower()
                or query in item.name.lower()
                or query in item.description.lower()
                or any(query in c.value for c in item.categories)
            ):
                results.append(item)
        return results

    # --- Mutate ---

    def add_candidate(self, item: RegistryItem) -> bool:
        """Add a candidate, deduplicating by id. Returns True if new."""
        candidates = self.load_candidates()
        existing_ids = {c.id for c in candidates}
        installed_ids = {i.id for i in self.load_installed()}
        rejected_ids = {r.id for r in self.load_rejected()}

        if item.id in existing_ids or item.id in installed_ids or item.id in rejected_ids:
            return False

        item.status = ItemStatus.CANDIDATE
        candidates.append(item)
        self.save_candidates(candidates)
        return True

    def install_item(self, item_id: str) -> bool:
        """Move a candidate to installed."""
        candidates = self.load_candidates()
        installed = self.load_installed()
        target = None
        remaining = []
        for c in candidates:
            if c.id == item_id:
                target = c
            else:
                remaining.append(c)
        if not target:
            return False
        target.status = ItemStatus.INSTALLED
        target.updated_at = datetime.now(timezone.utc)
        installed.append(target)
        self.save_installed(installed)
        self.save_candidates(remaining)
        return True

    def reject_item(self, item_id: str, reason: str = "") -> bool:
        """Move a candidate to rejected."""
        candidates = self.load_candidates()
        rejected = self.load_rejected()
        target = None
        remaining = []
        for c in candidates:
            if c.id == item_id:
                target = c
            else:
                remaining.append(c)
        if not target:
            return False
        target.status = ItemStatus.REJECTED
        target.local_notes = reason
        target.updated_at = datetime.now(timezone.utc)
        rejected.append(target)
        self.save_rejected(rejected)
        self.save_candidates(remaining)
        return True

    def deduplicate_candidates(self) -> int:
        """Remove duplicate candidates. Returns count of removed duplicates."""
        candidates = self.load_candidates()
        installed_ids = {i.id for i in self.load_installed()}
        seen: set[str] = set()
        unique: list[RegistryItem] = []
        removed = 0
        for c in candidates:
            key = c.id
            if key in seen or key in installed_ids:
                removed += 1
            else:
                seen.add(key)
                unique.append(c)
        if removed > 0:
            self.save_candidates(unique)
        return removed


class SnapshotManager:
    """Manages point-in-time registry snapshots."""

    def __init__(self, registry_dir: Path | None = None, snapshots_dir: Path | None = None):
        self.registry_dir = registry_dir or REGISTRY_DIR
        self.snapshots_dir = snapshots_dir or Path("snapshots")

    def create_snapshot(self, description: str = "", trigger: str = "") -> Snapshot:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        short_id = uuid.uuid4().hex[:6]
        snap_id = f"snap-{ts}-{short_id}"
        snap_dir = self.snapshots_dir / snap_id

        snap_dir.mkdir(parents=True, exist_ok=True)

        manifest: list[str] = []
        for f in self.registry_dir.rglob("*.yaml"):
            rel = f.relative_to(self.registry_dir)
            dest = snap_dir / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dest)
            manifest.append(str(rel))

        snap = Snapshot(
            id=snap_id,
            description=description or f"Snapshot at {ts}",
            trigger=trigger,
            file_manifest=manifest,
        )
        _save_yaml(snap_dir / "snapshot.yaml", snap.model_dump(mode="json"))
        return snap

    def list_snapshots(self) -> list[Snapshot]:
        snapshots = []
        if not self.snapshots_dir.exists():
            return snapshots
        for d in sorted(self.snapshots_dir.iterdir()):
            meta = d / "snapshot.yaml"
            if meta.exists():
                raw = _load_yaml(meta)
                if raw:
                    snapshots.append(Snapshot(**raw))
        return snapshots

    def rollback(self, snapshot_id: str) -> bool:
        snap_dir = self.snapshots_dir / snapshot_id
        if not snap_dir.exists():
            return False

        # Create a pre-rollback snapshot first
        self.create_snapshot(
            description=f"Pre-rollback backup before restoring {snapshot_id}",
            trigger=f"pre-rollback:{snapshot_id}",
        )

        # Restore registry files from snapshot
        for f in snap_dir.rglob("*.yaml"):
            if f.name == "snapshot.yaml":
                continue
            rel = f.relative_to(snap_dir)
            dest = self.registry_dir / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dest)

        return True
