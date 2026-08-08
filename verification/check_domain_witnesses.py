#!/usr/bin/env python3
"""Check two distinct instantiations of the generic witness algebra.

1. Lipschitz counterexample: shared JSON -> NumPy observable and Lean witness.
2. Dependency topology: shared JSON -> executable graph mutation and Lean witness.

This checker does not prove the Lean theorems; the Lean build does that. It checks
that both formal witnesses are explicitly bound to the current shared source and
that the independent executable observations agree with the registered source.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
ROOT = Path(os.environ.get("BASILISK_ROOT", DEFAULT_ROOT)).resolve()
VERIFY = ROOT / "verification"
sys.path.insert(0, str(VERIFY))
from dependency_mutator import evaluate as evaluate_dependency  # noqa: E402


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_source_receipt(spec: Path, lean: Path, errors: list[str]) -> None:
    receipt = sha256_file(spec)
    text = lean.read_text(encoding="utf-8")
    if receipt not in text:
        errors.append(f"{lean.name}: source receipt does not match {spec.name}: {receipt}")


def lipschitz_numpy(spec: dict) -> dict:
    labels = list(spec["carrier"])
    index = {label: i for i, label in enumerate(labels)}
    n = len(labels)
    d = np.ones((n, n), dtype=float) - np.eye(n, dtype=float)
    mapped = np.array([index[spec["map"][label]] for label in labels], dtype=int)

    ratios: list[float] = []
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            dx = d[i, j]
            dy = d[mapped[i], mapped[j]]
            ratios.append(float(dy / dx))

    preserves = all(
        (not bool(spec["source_predicate"][label]))
        or bool(spec["target_predicate"][spec["map"][label]])
        for label in labels
    )
    return {
        "lipschitz_constant": max(ratios, default=0.0),
        "preserves_predicate": bool(preserves),
    }


def main() -> int:
    errors: list[str] = []
    claims = json.loads((VERIFY / "claims.json").read_text(encoding="utf-8"))
    statuses = {c["id"]: c["status"] for c in claims.get("claims", [])}

    lip_path = VERIFY / "lipschitz_counterexample.json"
    lip = json.loads(lip_path.read_text(encoding="utf-8"))
    lip_observed = lipschitz_numpy(lip)
    if lip_observed != lip["expected"]:
        errors.append(f"C-MATH-001 NumPy disagreement: {lip_observed} != {lip['expected']}")
    if statuses.get(lip["claim_id"]) != "lean_theorem":
        errors.append("C-MATH-001 is no longer typed as lean_theorem")
    lip_lean = ROOT / "formal" / "Basilisk" / "LipschitzWitness.lean"
    require_source_receipt(lip_path, lip_lean, errors)
    lip_text = lip_lean.read_text(encoding="utf-8")
    for token in ("collapseToBad", "IsLipschitzNat", "PreservesPredicate"):
        if token not in lip_text:
            errors.append(f"LipschitzWitness.lean missing registered semantic token {token}")

    dep_path = VERIFY / "dependency_mutation.json"
    dep = json.loads(dep_path.read_text(encoding="utf-8"))
    dep_result = evaluate_dependency(dep)
    dep_observed = {key: dep_result[key] for key in dep["expected"]}
    if dep_observed != dep["expected"]:
        errors.append(f"C-MATH-007 mutation disagreement: {dep_observed} != {dep['expected']}")
    if statuses.get(dep["claim_id"]) != "lean_theorem":
        errors.append("C-MATH-007 is not typed as lean_theorem")
    dep_lean = ROOT / "formal" / "Basilisk" / "DependencyMutationWitness.lean"
    require_source_receipt(dep_path, dep_lean, errors)
    dep_text = dep_lean.read_text(encoding="utf-8")
    required = (".x, .child => true", ".coparent, .child => true", "dependency_mutation_adds_coparent")
    for token in required:
        if token not in dep_text:
            errors.append(f"DependencyMutationWitness.lean missing registered mutation token {token}")

    if errors:
        print("DOMAIN WITNESS CHECK: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("DOMAIN WITNESS CHECK: PASS — Lipschitz and dependency instances agree across substrates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
