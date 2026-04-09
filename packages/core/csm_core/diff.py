"""Diff generation for proposals and item comparisons."""

from __future__ import annotations

from typing import Any

from .models import RegistryItem


def diff_items(a: RegistryItem, b: RegistryItem) -> dict[str, Any]:
    """Compare two registry items and return a structured diff."""
    a_dict = a.model_dump(mode="json", exclude={"created_at", "updated_at"})
    b_dict = b.model_dump(mode="json", exclude={"created_at", "updated_at"})

    changes: dict[str, Any] = {}
    all_keys = set(a_dict.keys()) | set(b_dict.keys())

    for key in sorted(all_keys):
        val_a = a_dict.get(key)
        val_b = b_dict.get(key)
        if val_a != val_b:
            changes[key] = {"from": val_a, "to": val_b}

    return {
        "item_a": a.id,
        "item_b": b.id,
        "changes": changes,
        "summary": _summarize_diff(changes),
    }


def _summarize_diff(changes: dict[str, Any]) -> str:
    if not changes:
        return "Items are identical."
    parts = []
    for key, delta in changes.items():
        parts.append(f"  {key}: {_short(delta['from'])} -> {_short(delta['to'])}")
    return f"{len(changes)} field(s) differ:\n" + "\n".join(parts)


def _short(val: Any, max_len: int = 60) -> str:
    s = str(val)
    return s if len(s) <= max_len else s[: max_len - 3] + "..."


def diff_registry_state(before: list[RegistryItem], after: list[RegistryItem]) -> dict[str, Any]:
    """Diff two registry states (e.g., before/after a proposal apply)."""
    before_map = {i.id: i for i in before}
    after_map = {i.id: i for i in after}

    added = [i.id for i in after if i.id not in before_map]
    removed = [i.id for i in before if i.id not in after_map]
    modified = []
    for item_id in set(before_map) & set(after_map):
        d = diff_items(before_map[item_id], after_map[item_id])
        if d["changes"]:
            modified.append(d)

    return {
        "added": added,
        "removed": removed,
        "modified": modified,
        "summary": f"+{len(added)} -{len(removed)} ~{len(modified)}",
    }
