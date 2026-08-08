#!/usr/bin/env python3
"""Check distinct instantiations of the generic witness algebra."""

from __future__ import annotations

import hashlib
import json
import math
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


def validate_lipschitz_spec(spec: dict) -> list[str]:
    errors: list[str] = []
    if spec.get("schema_version") != 1:
        errors.append(f"unsupported Lipschitz schema_version: {spec.get('schema_version')!r}")
    carrier = spec.get("carrier")
    if not isinstance(carrier, list) or len(carrier) < 2:
        return errors + ["Lipschitz carrier must contain at least two labels"]
    if any(not isinstance(label, str) or not label for label in carrier):
        errors.append("Lipschitz carrier labels must be non-empty strings")
    if len(carrier) != len(set(carrier)):
        errors.append("Lipschitz carrier labels must be unique")
    labels = set(carrier)
    if spec.get("distance") != "discrete":
        errors.append(f"unsupported Lipschitz witness distance: {spec.get('distance')!r}")

    mapping = spec.get("map")
    if not isinstance(mapping, dict) or set(mapping) != labels:
        errors.append("Lipschitz map must be total with exactly one entry per carrier label")
    elif any(value not in labels for value in mapping.values()):
        errors.append("Lipschitz map must map every label back into the carrier")

    for field in ("source_predicate", "target_predicate"):
        predicate = spec.get(field)
        if not isinstance(predicate, dict) or set(predicate) != labels:
            errors.append(f"{field} must be total on the carrier")
        elif any(type(value) is not bool for value in predicate.values()):
            errors.append(f"{field} values must be Boolean")

    expected = spec.get("expected")
    if not isinstance(expected, dict) or set(expected) != {"lipschitz_constant", "preserves_predicate"}:
        errors.append("Lipschitz expected must contain exactly lipschitz_constant and preserves_predicate")
    else:
        constant = expected.get("lipschitz_constant")
        if not isinstance(constant, (int, float)) or isinstance(constant, bool) or not math.isfinite(float(constant)) or float(constant) < 0:
            errors.append("expected Lipschitz constant must be a finite nonnegative number")
        if type(expected.get("preserves_predicate")) is not bool:
            errors.append("expected preserves_predicate must be Boolean")
    return errors


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
    errors.extend(validate_lipschitz_spec(lip))
    if not errors:
        lip_observed = lipschitz_numpy(lip)
        if lip_observed != lip["expected"]:
            errors.append(f"C-MATH-001 NumPy disagreement: {lip_observed} != {lip['expected']}")
    if statuses.get(lip.get("claim_id")) != "lean_theorem":
        errors.append("C-MATH-001 is no longer typed as lean_theorem")
    lip_lean = ROOT / "formal" / "Basilisk" / "LipschitzWitness.lean"
    require_source_receipt(lip_path, lip_lean, errors)
    lip_text = lip_lean.read_text(encoding="utf-8")
    for token in ("collapseToBad", "IsLipschitzNat", "PreservesPredicate"):
        if token not in lip_text:
            errors.append(f"LipschitzWitness.lean missing registered semantic token {token}")

    dep_path = VERIFY / "dependency_mutation.json"
    dep = json.loads(dep_path.read_text(encoding="utf-8"))
    try:
        dep_result = evaluate_dependency(dep)
    except (ValueError, KeyError, TypeError) as exc:
        dep_result = None
        errors.append(f"C-MATH-007 malformed dependency witness: {exc}")
    if dep_result is not None:
        expected = dep.get("expected")
        if not isinstance(expected, dict) or not expected:
            errors.append("C-MATH-007 expected must be a non-empty object")
        else:
            unknown_expected = sorted(set(expected) - set(dep_result))
            if unknown_expected:
                errors.append(f"C-MATH-007 expected contains unknown observation keys: {unknown_expected}")
            dep_observed = {key: dep_result.get(key) for key in expected}
            if dep_observed != expected:
                errors.append(f"C-MATH-007 mutation disagreement: {dep_observed} != {expected}")
    if statuses.get(dep.get("claim_id")) != "lean_theorem":
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
