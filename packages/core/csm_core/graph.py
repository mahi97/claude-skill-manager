"""Graph operations for visualizing and querying registry relationships."""

from __future__ import annotations

from typing import Any

import networkx as nx

from .models import RegistryItem, Relationship


def build_graph(items: list[RegistryItem]) -> nx.DiGraph:
    """Build a directed graph from registry items and their relationships."""
    G = nx.DiGraph()

    for item in items:
        G.add_node(
            item.id,
            name=item.name,
            type=item.type.value,
            status=item.status.value,
            trust_tier=item.trust_tier.value,
            categories=[c.value for c in item.categories],
            risk_score=item.risk.score,
        )

    for item in items:
        for rel in item.relationships:
            G.add_edge(
                rel.source_id,
                rel.target_id,
                type=rel.type.value,
                notes=rel.notes,
            )

    return G


def export_graph_json(items: list[RegistryItem]) -> dict[str, Any]:
    """Export graph as JSON suitable for React Flow / Cytoscape."""
    G = build_graph(items)

    nodes = []
    for node_id, data in G.nodes(data=True):
        nodes.append({
            "id": node_id,
            "data": {
                "label": data.get("name", node_id),
                **data,
            },
            "position": {"x": 0, "y": 0},  # layout computed on frontend
        })

    edges = []
    for source, target, data in G.edges(data=True):
        edges.append({
            "id": f"{source}-{data.get('type', 'rel')}-{target}",
            "source": source,
            "target": target,
            "data": data,
            "label": data.get("type", ""),
        })

    return {"nodes": nodes, "edges": edges}


def find_conflicts(items: list[RegistryItem]) -> list[tuple[str, str, str]]:
    """Find items that conflict with each other."""
    conflicts = []
    for item in items:
        for rel in item.relationships:
            if rel.type.value == "conflicts_with":
                conflicts.append((rel.source_id, rel.target_id, rel.notes))
    return conflicts


def find_dependencies(items: list[RegistryItem], item_id: str) -> list[str]:
    """Find what an item depends on."""
    G = build_graph(items)
    deps = []
    for _, target, data in G.out_edges(item_id, data=True):
        if data.get("type") == "depends_on":
            deps.append(target)
    return deps
