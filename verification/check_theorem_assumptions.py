#!/usr/bin/env python3
"""Check the theorem-assumption exterior against the complete formal inventory.

Local Lean style treats explicit proof-premise binders as names beginning with
``h`` or ``_h``. Ordinary carrier, function, predicate, and data arguments are
parameters rather than theorem assumptions. This checker therefore discovers
all such proof-premise binders from every registered theorem/lemma signature and
requires one exact classification in ``theorem_assumptions.json``.

Substantive premises must carry a distinct, registered finite necessity witness
from AssumptionSurfaces.lean or AssumptionNecessity.lean. Structural and
definitional premises remain explicitly classified but do not require ceremonial
countermodels.
"""

from __future__ import annotations

import os
from pathlib import Path

from registry_io import load_registry_list, strict_load_json

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
ROOT = Path(os.environ.get("BASILISK_ROOT", DEFAULT_ROOT)).resolve()
VERIFICATION = ROOT / "verification"
REGISTRY = VERIFICATION / "theorem_assumptions.json"

ALLOWED_CATEGORIES = {"structural", "definitional", "substantive"}
NECESSITY_MODULES = {
    "formal/Basilisk/AssumptionSurfaces.lean",
    "formal/Basilisk/AssumptionNecessity.lean",
}


def conclusion_colon(signature: str) -> int:
    """Return the top-level colon separating binders from the conclusion."""
    depth = {"(": 0, "{": 0, "[": 0}
    matching = {")": "(", "}": "{", "]": "["}
    in_string = False
    escaped = False
    for i, ch in enumerate(signature):
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
            continue
        if ch in depth:
            depth[ch] += 1
            continue
        if ch in matching:
            opener = matching[ch]
            depth[opener] -= 1
            continue
        if ch == ":" and all(v == 0 for v in depth.values()):
            return i
    raise ValueError(f"registered theorem signature lacks top-level conclusion colon: {signature}")


def top_level_binder_groups(prefix: str) -> list[str]:
    """Extract top-level (...) and {...} binder bodies from a theorem prefix."""
    out: list[str] = []
    i = 0
    while i < len(prefix):
        if prefix[i] not in "({":
            i += 1
            continue
        opener = prefix[i]
        closer = ")" if opener == "(" else "}"
        start = i + 1
        depth = 1
        i += 1
        in_string = False
        escaped = False
        while i < len(prefix) and depth:
            ch = prefix[i]
            if in_string:
                if escaped:
                    escaped = False
                elif ch == "\\":
                    escaped = True
                elif ch == '"':
                    in_string = False
                i += 1
                continue
            if ch == '"':
                in_string = True
            elif ch == opener:
                depth += 1
            elif ch == closer:
                depth -= 1
                if depth == 0:
                    out.append(prefix[start:i].strip())
                    i += 1
                    break
            i += 1
        if depth:
            raise ValueError(f"unbalanced binder group in signature prefix: {prefix}")
    return out


def premise_binders(signature: str) -> list[str]:
    prefix = signature[: conclusion_colon(signature)]
    names: list[str] = []
    for body in top_level_binder_groups(prefix):
        if ":" not in body:
            continue
        lhs, _rhs = body.split(":", 1)
        for raw in lhs.split():
            name = raw.strip()
            if name.startswith("h") or name.startswith("_h"):
                names.append(name)
    return names


def main() -> int:
    errors: list[str] = []
    formal_entries, _shards = load_registry_list(
        VERIFICATION,
        base_name="formal_inventory.json",
        shard_prefix="formal_inventory_",
        payload_key="formal_claims",
        errors=errors,
    )

    try:
        doc = strict_load_json(REGISTRY)
    except Exception as exc:
        print("THEOREM ASSUMPTION CHECK: FAIL")
        print(f"- theorem_assumptions.json malformed: {exc}")
        return 1
    rows = doc.get("assumptions", []) if isinstance(doc, dict) else []
    if not isinstance(rows, list):
        errors.append("theorem_assumptions.json: assumptions must be a list")
        rows = []

    theorem_by_key: dict[tuple[str, str], dict] = {}
    symbol_entries: dict[str, list[dict]] = {}
    discovered: set[tuple[str, str, str]] = set()
    for entry in formal_entries:
        module = entry.get("module")
        symbol = entry.get("symbol")
        signature = entry.get("signature")
        if not all(isinstance(x, str) and x for x in (module, symbol, signature)):
            errors.append(f"malformed formal inventory entry: {entry!r}")
            continue
        theorem_by_key[(module, symbol)] = entry
        symbol_entries.setdefault(symbol, []).append(entry)
        try:
            binders = premise_binders(signature)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if len(binders) != len(set(binders)):
            errors.append(f"{module}:{symbol}: duplicate proof-premise binder names")
        for binder in binders:
            discovered.add((module, symbol, binder))

    registered: dict[tuple[str, str, str], dict] = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"assumptions[{index}] must be an object")
            continue
        key = (row.get("module"), row.get("symbol"), row.get("binder"))
        if not all(isinstance(x, str) and x for x in key):
            errors.append(f"assumptions[{index}] missing string module/symbol/binder")
            continue
        if key in registered:
            errors.append(f"duplicate assumption classification: {key}")
            continue
        registered[key] = row
        if (key[0], key[1]) not in theorem_by_key:
            errors.append(f"stale assumption row has no registered theorem: {key[0]}:{key[1]}")
        category = row.get("category")
        if category not in ALLOWED_CATEGORIES:
            errors.append(f"{key}: invalid category {category!r}")
        if not isinstance(row.get("rationale"), str) or not row["rationale"].strip():
            errors.append(f"{key}: rationale must be nonempty")

        evidence = row.get("evidence_symbol")
        if category == "substantive":
            if not isinstance(evidence, str) or not evidence:
                errors.append(f"{key}: substantive premise lacks evidence_symbol")
                continue
            candidates = symbol_entries.get(evidence, [])
            if len(candidates) != 1:
                errors.append(
                    f"{key}: evidence_symbol {evidence!r} must resolve to exactly one formal theorem"
                )
                continue
            witness = candidates[0]
            if witness.get("module") not in NECESSITY_MODULES:
                errors.append(
                    f"{key}: substantive witness {evidence} must live in an assumption-necessity module"
                )
            if witness.get("module") == key[0] and witness.get("symbol") == key[1]:
                errors.append(f"{key}: theorem cannot witness necessity of its own premise")
        elif evidence is not None:
            errors.append(f"{key}: non-substantive premise must use evidence_symbol null")

    missing = sorted(discovered - set(registered))
    stale = sorted(set(registered) - discovered)
    for key in missing:
        errors.append(f"unclassified theorem premise: {key[0]}:{key[1]}:{key[2]}")
    for key in stale:
        errors.append(f"registered assumption binder no longer exists: {key[0]}:{key[1]}:{key[2]}")

    if errors:
        print("THEOREM ASSUMPTION CHECK: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    counts = {category: 0 for category in sorted(ALLOWED_CATEGORIES)}
    for row in rows:
        counts[row["category"]] += 1
    print(
        "THEOREM ASSUMPTION CHECK: PASS — "
        f"{len(formal_entries)} formal declarations, {len(discovered)} proof premises; "
        + ", ".join(f"{k}={counts[k]}" for k in sorted(counts))
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
