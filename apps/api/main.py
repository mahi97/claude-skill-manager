"""CSM API - FastAPI backend for Claude Skill Manager."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure packages are importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "core"))
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "connectors"))
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "agents"))

import asyncio

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from csm_agents.applier import ApplyAgent
from csm_agents.pipeline import PipelineAgent
from csm_core.diff import diff_items
from csm_core.graph import export_graph_json
from csm_core.registry import Registry, SnapshotManager

REGISTRY_DIR = PROJECT_ROOT / "registry"
SNAPSHOTS_DIR = PROJECT_ROOT / "snapshots"

app = FastAPI(
    title="Claude Skill Manager API",
    description="REST API for managing Claude Code ecosystem components",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_registry() -> Registry:
    return Registry(REGISTRY_DIR)


def get_snapshot_mgr() -> SnapshotManager:
    return SnapshotManager(REGISTRY_DIR, SNAPSHOTS_DIR)


# --- Registry endpoints ---


@app.get("/api/status")
def status():
    reg = get_registry()
    snap_mgr = get_snapshot_mgr()
    return {
        "installed": len(reg.load_installed()),
        "candidates": len(reg.load_candidates()),
        "rejected": len(reg.load_rejected()),
        "sources": len(reg.load_sources()),
        "proposals": len(reg.load_proposals()),
        "evaluations": len(reg.load_evaluations()),
        "snapshots": len(snap_mgr.list_snapshots()),
    }


@app.get("/api/items")
def list_items(status: str | None = None, type: str | None = None, category: str | None = None):
    reg = get_registry()
    items = reg.get_all_items()
    if status:
        items = [i for i in items if i.status.value == status]
    if type:
        items = [i for i in items if i.type.value == type]
    if category:
        items = [i for i in items if any(c.value == category for c in i.categories)]
    return [i.model_dump(mode="json") for i in items]


@app.get("/api/items/installed")
def list_installed():
    reg = get_registry()
    return [i.model_dump(mode="json") for i in reg.load_installed()]


@app.get("/api/items/candidates")
def list_candidates():
    reg = get_registry()
    return [i.model_dump(mode="json") for i in reg.load_candidates()]


@app.get("/api/items/{item_id}")
def get_item(item_id: str):
    reg = get_registry()
    item = reg.find_item(item_id)
    if not item:
        raise HTTPException(404, f"Item not found: {item_id}")
    return item.model_dump(mode="json")


@app.get("/api/items/{item_a}/compare/{item_b}")
def compare_items(item_a: str, item_b: str):
    reg = get_registry()
    a = reg.find_item(item_a)
    b = reg.find_item(item_b)
    if not a:
        raise HTTPException(404, f"Item not found: {item_a}")
    if not b:
        raise HTTPException(404, f"Item not found: {item_b}")
    return diff_items(a, b)


@app.get("/api/search")
def search(q: str):
    reg = get_registry()
    results = reg.search_items(q)
    return [i.model_dump(mode="json") for i in results]


# --- Sources ---


@app.get("/api/sources")
def list_sources():
    reg = get_registry()
    return [s.model_dump(mode="json") for s in reg.load_sources()]


# --- Graph ---


@app.get("/api/graph")
def get_graph():
    reg = get_registry()
    return export_graph_json(reg.get_all_items())


# --- Proposals ---


@app.get("/api/proposals")
def list_proposals():
    reg = get_registry()
    return [p.model_dump(mode="json") for p in reg.load_proposals()]


@app.get("/api/proposals/{proposal_id}")
def get_proposal(proposal_id: str):
    reg = get_registry()
    proposals = reg.load_proposals()
    proposal = next((p for p in proposals if p.id == proposal_id), None)
    if not proposal:
        raise HTTPException(404, f"Proposal not found: {proposal_id}")
    return proposal.model_dump(mode="json")


@app.post("/api/proposals/{proposal_id}/apply")
def apply_proposal(proposal_id: str):
    reg = get_registry()
    snap_mgr = get_snapshot_mgr()
    applier = ApplyAgent(reg, snap_mgr)
    result = applier.apply_proposal(proposal_id)
    if not result["success"]:
        raise HTTPException(400, result)
    return result


# --- Evaluations ---


@app.get("/api/evaluations")
def list_evaluations():
    reg = get_registry()
    return [e.model_dump(mode="json") for e in reg.load_evaluations()]


# --- Snapshots ---


@app.get("/api/snapshots")
def list_snapshots():
    snap_mgr = get_snapshot_mgr()
    return [s.model_dump(mode="json") for s in snap_mgr.list_snapshots()]


@app.post("/api/snapshots")
def create_snapshot(description: str = "Manual snapshot"):
    snap_mgr = get_snapshot_mgr()
    snap = snap_mgr.create_snapshot(description=description, trigger="api")
    return snap.model_dump(mode="json")


@app.post("/api/snapshots/{snapshot_id}/rollback")
def rollback_snapshot(snapshot_id: str):
    snap_mgr = get_snapshot_mgr()
    ok = snap_mgr.rollback(snapshot_id)
    if not ok:
        raise HTTPException(404, f"Snapshot not found: {snapshot_id}")
    return {"success": True, "rolled_back_to": snapshot_id}


# --- Pipeline ---


@app.post("/api/scout")
async def run_scout():
    reg = get_registry()
    pipeline = PipelineAgent(reg)
    results = await pipeline.scout.scout_all()
    return {
        "sources_checked": len(results),
        "new_candidates": {src: len(items) for src, items in results.items()},
        "total_new": sum(len(items) for items in results.values()),
    }


@app.post("/api/evaluate")
def run_evaluate():
    reg = get_registry()
    pipeline = PipelineAgent(reg)
    reports = pipeline.evaluate_candidates()
    return {
        "evaluated": len(reports),
        "reports": [r.model_dump(mode="json") for r in reports],
    }


@app.post("/api/propose")
def run_propose():
    reg = get_registry()
    pipeline = PipelineAgent(reg)
    pipeline.evaluate_candidates()
    proposals = pipeline.generate_proposals()
    return {
        "generated": len(proposals),
        "proposals": [p.model_dump(mode="json") for p in proposals],
    }


# --- Taxonomy ---


@app.get("/api/taxonomy")
def get_taxonomy():
    reg = get_registry()
    return [t.model_dump(mode="json") for t in reg.load_taxonomy()]


# --- Policies ---


@app.get("/api/policies")
def get_policies():
    reg = get_registry()
    return [p.model_dump(mode="json") for p in reg.load_policies()]
