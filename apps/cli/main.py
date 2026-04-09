"""CSM CLI - Terminal interface for Claude Skill Manager."""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

# Ensure packages are importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "packages" / "core"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "packages" / "connectors"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "packages" / "agents"))

from csm_agents.applier import ApplyAgent
from csm_agents.pipeline import PipelineAgent
from csm_core.diff import diff_items
from csm_core.evaluator import evaluate_item
from csm_core.graph import export_graph_json
from csm_core.models import ItemStatus
from csm_core.registry import Registry, SnapshotManager

app = typer.Typer(name="csm", help="Claude Skill Manager - manage your Claude Code ecosystem")
console = Console()

# Resolve project root relative to this file
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
REGISTRY_DIR = PROJECT_ROOT / "registry"
SNAPSHOTS_DIR = PROJECT_ROOT / "snapshots"


def get_registry() -> Registry:
    return Registry(REGISTRY_DIR)


def get_snapshot_mgr() -> SnapshotManager:
    return SnapshotManager(REGISTRY_DIR, SNAPSHOTS_DIR)


@app.command()
def init():
    """Initialize or verify the CSM registry."""
    reg = get_registry()
    installed = reg.load_installed()
    candidates = reg.load_candidates()
    sources = reg.load_sources()

    console.print(Panel.fit(
        f"[bold green]CSM Registry Initialized[/]\n\n"
        f"  Installed items: {len(installed)}\n"
        f"  Candidates:      {len(candidates)}\n"
        f"  Sources:         {len(sources)}\n"
        f"  Registry path:   {REGISTRY_DIR}",
        title="Claude Skill Manager",
    ))


@app.command()
def search(query: str):
    """Search the registry for items matching a query."""
    reg = get_registry()
    results = reg.search_items(query)

    if not results:
        console.print(f"[yellow]No results for '{query}'[/]")
        return

    table = Table(title=f"Search: '{query}'")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="bold")
    table.add_column("Type")
    table.add_column("Status")
    table.add_column("Trust")
    table.add_column("Risk", justify="right")

    for item in results:
        status_color = {"installed": "green", "candidate": "yellow", "rejected": "red"}.get(item.status.value, "white")
        table.add_row(
            item.id,
            item.name,
            item.type.value,
            f"[{status_color}]{item.status.value}[/]",
            item.trust_tier.value,
            f"{item.risk.score:.2f}",
        )

    console.print(table)


@app.command()
def inspect(item_id: str):
    """Inspect a specific registry item in detail."""
    reg = get_registry()
    item = reg.find_item(item_id)

    if not item:
        console.print(f"[red]Item not found: {item_id}[/]")
        raise typer.Exit(1)

    trust_color = {"official": "green", "curated": "blue", "community": "yellow", "untrusted": "red"}.get(
        item.trust_tier.value, "white"
    )

    lines = [
        f"[bold]{item.name}[/] ({item.type.value})",
        f"Status: [{trust_color}]{item.status.value}[/]",
        f"Trust:  [{trust_color}]{item.trust_tier.value}[/]",
        f"Risk:   {item.risk.score:.2f}",
        "",
        f"[dim]Description:[/] {item.description}",
        f"[dim]Source:[/]      {item.source_url}",
        f"[dim]Version:[/]     {item.version}",
        f"[dim]Categories:[/]  {', '.join(c.value for c in item.categories)}",
    ]

    if item.risk.flags:
        lines.append(f"[dim]Risk flags:[/]  {', '.join(f.value for f in item.risk.flags)}")

    if item.relationships:
        lines.append("")
        lines.append("[dim]Relationships:[/]")
        for rel in item.relationships:
            lines.append(f"  {rel.type.value} -> {rel.target_id}")

    if item.local_notes:
        lines.append(f"\n[dim]Notes:[/] {item.local_notes}")

    console.print(Panel("\n".join(lines), title=f"Item: {item.id}"))


@app.command()
def compare(item_a: str, item_b: str):
    """Compare two registry items side by side."""
    reg = get_registry()
    a = reg.find_item(item_a)
    b = reg.find_item(item_b)

    if not a:
        console.print(f"[red]Item not found: {item_a}[/]")
        raise typer.Exit(1)
    if not b:
        console.print(f"[red]Item not found: {item_b}[/]")
        raise typer.Exit(1)

    d = diff_items(a, b)

    table = Table(title=f"Compare: {item_a} vs {item_b}")
    table.add_column("Field", style="cyan")
    table.add_column(item_a, style="green")
    table.add_column(item_b, style="blue")

    for field, delta in d["changes"].items():
        table.add_row(field, str(delta["from"])[:60], str(delta["to"])[:60])

    if not d["changes"]:
        console.print("[green]Items are identical.[/]")
    else:
        console.print(table)


@app.command()
def scout():
    """Scout all enabled sources for new items."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    reg = get_registry()
    pipeline = PipelineAgent(reg)

    console.print("[bold]Scouting sources...[/]")
    results = asyncio.run(pipeline.scout.scout_all())

    total = sum(len(items) for items in results.values())
    for src_id, items in results.items():
        if items:
            console.print(f"  [green]{src_id}[/]: {len(items)} new items")
        else:
            console.print(f"  [dim]{src_id}[/]: no new items")

    console.print(f"\n[bold]Total new candidates: {total}[/]")


@app.command()
def evaluate():
    """Evaluate all unevaluated candidates."""
    reg = get_registry()
    pipeline = PipelineAgent(reg)
    reports = pipeline.evaluate_candidates()

    if not reports:
        console.print("[yellow]No unevaluated candidates found.[/]")
        return

    table = Table(title="Evaluation Results")
    table.add_column("Item", style="cyan")
    table.add_column("Score", justify="right")
    table.add_column("Recommendation")
    table.add_column("Overlap")

    for r in reports:
        rec_color = {"Recommend install": "green", "Review manually": "yellow", "Not recommended": "red"}.get(
            r.recommendation, "white"
        )
        table.add_row(
            r.item_id,
            f"{r.overall_score:.3f}",
            f"[{rec_color}]{r.recommendation}[/]",
            ", ".join(r.overlap_with) or "-",
        )

    console.print(table)


@app.command()
def propose():
    """Generate proposals for evaluated candidates."""
    reg = get_registry()
    pipeline = PipelineAgent(reg)

    # Evaluate first if needed
    pipeline.evaluate_candidates()
    proposals = pipeline.generate_proposals()

    if not proposals:
        console.print("[yellow]No proposals to generate.[/]")
        return

    for p in proposals:
        status_color = "yellow" if p.status.value == "pending" else "green"
        console.print(Panel(
            f"[bold]{p.title}[/]\n\n"
            f"{p.summary}\n\n"
            f"[dim]Recommendation:[/] {p.recommendation}\n"
            f"[dim]Risk:[/] {p.risk_summary}\n"
            f"[dim]Overlap:[/] {p.overlap_analysis}\n"
            f"[dim]Impact:[/] {p.workflow_impact}",
            title=f"[{status_color}]Proposal: {p.id}[/]",
        ))


@app.command()
def apply(proposal_id: str):
    """Apply a pending proposal (creates snapshot first)."""
    reg = get_registry()
    snap_mgr = get_snapshot_mgr()
    applier = ApplyAgent(reg, snap_mgr)

    console.print(f"[bold]Applying proposal: {proposal_id}[/]")
    result = applier.apply_proposal(proposal_id)

    if result["success"]:
        console.print(f"[green]Proposal applied successfully.[/]")
        console.print(f"  Snapshot: {result['snapshot_id']}")
        console.print(f"  Applied:  {', '.join(result['applied'])}")
    else:
        console.print(f"[red]Errors during apply:[/]")
        for err in result.get("errors", []):
            console.print(f"  - {err}")


@app.command()
def snapshot(description: str = "Manual snapshot"):
    """Create a point-in-time registry snapshot."""
    snap_mgr = get_snapshot_mgr()
    snap = snap_mgr.create_snapshot(description=description, trigger="manual")
    console.print(f"[green]Snapshot created: {snap.id}[/]")
    console.print(f"  Files: {len(snap.file_manifest)}")


@app.command()
def rollback(snapshot_id: str):
    """Rollback registry to a previous snapshot."""
    snap_mgr = get_snapshot_mgr()
    ok = snap_mgr.rollback(snapshot_id)
    if ok:
        console.print(f"[green]Rolled back to {snapshot_id}[/]")
    else:
        console.print(f"[red]Snapshot not found: {snapshot_id}[/]")
        raise typer.Exit(1)


@app.command("graph")
def graph_export(
    output: str = typer.Option("graph.json", help="Output file path"),
    format: str = typer.Option("json", help="Output format (json)"),
):
    """Export the registry graph."""
    reg = get_registry()
    items = reg.get_all_items()
    graph_data = export_graph_json(items)

    out_path = Path(output)
    with open(out_path, "w") as f:
        json.dump(graph_data, f, indent=2)

    console.print(f"[green]Graph exported to {out_path}[/]")
    console.print(f"  Nodes: {len(graph_data['nodes'])}")
    console.print(f"  Edges: {len(graph_data['edges'])}")


@app.command()
def serve(
    host: str = typer.Option("127.0.0.1", help="API host"),
    port: int = typer.Option(8000, help="API port"),
):
    """Start the API server."""
    import uvicorn
    console.print(f"[bold]Starting CSM API at http://{host}:{port}[/]")
    uvicorn.run("apps.api.main:app", host=host, port=port, reload=True)


@app.command()
def status():
    """Show a summary of the current registry state."""
    reg = get_registry()
    snap_mgr = get_snapshot_mgr()

    installed = reg.load_installed()
    candidates = reg.load_candidates()
    rejected = reg.load_rejected()
    sources = reg.load_sources()
    proposals = reg.load_proposals()
    snapshots = snap_mgr.list_snapshots()

    tree = Tree("[bold]CSM Registry Status[/]")

    inst_branch = tree.add(f"[green]Installed ({len(installed)})[/]")
    for item in installed:
        inst_branch.add(f"{item.name} [{item.type.value}] - {item.trust_tier.value}")

    cand_branch = tree.add(f"[yellow]Candidates ({len(candidates)})[/]")
    for item in candidates:
        cand_branch.add(f"{item.name} [{item.type.value}] - risk:{item.risk.score:.2f}")

    rej_branch = tree.add(f"[red]Rejected ({len(rejected)})[/]")
    for item in rejected:
        rej_branch.add(f"{item.name}")

    src_branch = tree.add(f"[blue]Sources ({len(sources)})[/]")
    for s in sources:
        status = "enabled" if s.enabled else "disabled"
        src_branch.add(f"{s.name} ({s.type.value}) [{status}]")

    prop_branch = tree.add(f"[magenta]Proposals ({len(proposals)})[/]")
    for p in proposals:
        prop_branch.add(f"{p.title} [{p.status.value}]")

    snap_branch = tree.add(f"[cyan]Snapshots ({len(snapshots)})[/]")
    for s in snapshots:
        snap_branch.add(f"{s.id}: {s.description}")

    console.print(tree)


if __name__ == "__main__":
    app()
