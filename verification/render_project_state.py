#!/usr/bin/env python3
"""Render/check a human-readable project state from canonical registries."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from registry_io import strict_load_json

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
ROOT = Path(os.environ.get("BASILISK_ROOT", DEFAULT_ROOT)).resolve()
CLAIMS = ROOT / "verification" / "claims.json"
FRONTIER = ROOT / "verification" / "completeness_frontier.json"
CLOSURES = ROOT / "verification" / "frontier_closures.json"
SCOPE = ROOT / "verification" / "scope_registry.json"
OUTPUT = ROOT / "docs" / "project-state.md"


def render() -> str:
    claims_doc = strict_load_json(CLAIMS)
    frontier_doc = strict_load_json(FRONTIER)
    closures_doc = strict_load_json(CLOSURES)
    scope_doc = strict_load_json(SCOPE)

    claims = {row["id"]: row for row in claims_doc["claims"]}
    frontier = {row["id"]: row for row in frontier_doc["frontier"]}
    closures = {row["id"]: row for row in closures_doc["closures"]}
    claim_scope = {row["id"]: row for row in scope_doc["claim_scope"]}
    frontier_scope = {row["id"]: row for row in scope_doc["frontier_scope"]}

    by_layer: dict[str, list[str]] = {"core": [], "theory": [], "bridge": []}
    for cid, placement in claim_scope.items():
        by_layer[placement["layer"]].append(cid)
    for values in by_layer.values():
        values.sort()

    by_schedule: dict[str, list[str]] = {"active": [], "deferred": [], "parked": []}
    for fid, placement in frontier_scope.items():
        by_schedule[placement["schedule"]].append(fid)
    for values in by_schedule.values():
        values.sort()

    lines = [
        "# Project state",
        "",
        "> **Generated status surface.** This file is rendered from the canonical claim, scope, open-frontier, and closure registries. Edit those registries rather than hand-editing this page.",
        "",
        "## Claim surface",
        "",
        f"- **Core:** {len(by_layer['core'])} claims",
        f"- **Parameterized Transformation Theory:** {len(by_layer['theory'])} claims",
        f"- **Research Bridges:** {len(by_layer['bridge'])} claims",
        f"- **Total:** {len(claims)} claims",
        "",
    ]

    for layer, title in (
        ("core", "Core claims"),
        ("theory", "Theory claims"),
        ("bridge", "Bridge claims"),
    ):
        lines.extend([f"### {title}", ""])
        for cid in by_layer[layer]:
            lines.append(f"- `{cid}` — {claims[cid]['title']}")
        lines.append("")

    lines.extend(
        [
            "## Open frontier scheduling",
            "",
            f"- **Active Core debt:** {len(by_schedule['active'])}",
            f"- **Deferred Core debt:** {len(by_schedule['deferred'])}",
            f"- **Parked Bridge debt:** {len(by_schedule['parked'])}",
            "",
        ]
    )

    for schedule, title in (
        ("active", "Active"),
        ("deferred", "Deferred"),
        ("parked", "Parked"),
    ):
        lines.extend([f"### {title}", ""])
        for fid in by_schedule[schedule]:
            row = frontier[fid]
            placement = frontier_scope[fid]
            lines.append(f"- `{fid}` — **{row['surface']}** — {placement['reason']}")
        lines.append("")

    lines.extend(["## Closed frontier debt", ""])
    for fid in sorted(closures):
        row = closures[fid]
        claims_text = ", ".join(f"`{cid}`" for cid in row["closed_by_claims"])
        lines.append(f"- `{fid}` — **{row['surface']}** — closed by {claims_text}")
    lines.extend(
        [
            "",
            "## Consolidation rule",
            "",
            "During consolidation, only Core frontier items may be scheduled `active`. Deferred Core debt remains open; parked Bridge debt remains visible but is not a Core release requirement. See [`core-scope.md`](core-scope.md).",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = render()

    if args.check:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.is_file() else ""
        if current != text:
            print("PROJECT STATE CHECK: FAIL — docs/project-state.md is stale")
            return 1
        print("PROJECT STATE CHECK: PASS")
        return 0

    OUTPUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
