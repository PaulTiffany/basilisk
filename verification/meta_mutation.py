#!/usr/bin/env python3
"""Deliberately damage temporary copies and require verifier detection."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CHECKS = {
    "provenance": ROOT / "verification" / "check_provenance.py",
    "recursivity": ROOT / "verification" / "check_recursivity.py",
    "numeric": ROOT / "verification" / "check_numeric.py",
    "formal": ROOT / "verification" / "check_formal_closure.py",
    "controller": ROOT / "verification" / "check_controller_vectors.py",
    "cross": ROOT / "verification" / "check_cross_witness.py",
    "domain": ROOT / "verification" / "check_domain_witnesses.py",
    "witness": ROOT / "verification" / "check_witness_graph.py",
    "exterior": ROOT / "verification" / "check_exterior_coverage.py",
    "json": ROOT / "scripts" / "validate_json.py",
}


def clone_minimal(dst: Path) -> None:
    for name in ("verification", "formal", "docs", "evals", "src", "scripts", "spec", "examples"):
        src = ROOT / name
        if src.exists():
            shutil.copytree(src, dst / name)


def run_check(name: str, temp_root: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["BASILISK_ROOT"] = str(temp_root)
    return subprocess.run(
        [sys.executable, str(CHECKS[name])], env=env, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
    )


def mutate_bad_receipt(root: Path) -> None:
    path = root / "verification" / "bindings.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["bindings"][0]["sha256"] = "0" * 64
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def mutate_cycle(root: Path) -> None:
    path = root / "verification" / "claims.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    by_id = {c["id"]: c for c in doc["claims"]}
    by_id["C-MATH-001"]["depends_on"] = ["C-MATH-003"]
    by_id["C-MATH-003"]["depends_on"] = ["C-MATH-001"]
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def mutate_numeric_expected(root: Path) -> None:
    path = root / "verification" / "EXPECTED_NUMERIC.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["claims"]["C-MATH-001"]["observed_lipschitz_ratio"] = 999.0
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def mutate_remove_inventory_entry(root: Path) -> None:
    path = root / "verification" / "formal_inventory.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["formal_claims"] = [e for e in doc["formal_claims"] if e["symbol"] != "lipschitz_alone_not_constitutional"]
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def mutate_remove_root_import(root: Path) -> None:
    path = root / "formal" / "Basilisk.lean"
    text = path.read_text(encoding="utf-8").replace("import Basilisk.ConstitutionalLipschitz\n", "")
    path.write_text(text, encoding="utf-8")


def mutate_vector_expected_gate(root: Path) -> None:
    path = root / "verification" / "controller_vectors.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["cases"][0]["expected_gate"] = "stop"
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def mutate_lean_vector_transcription(root: Path) -> None:
    path = root / "formal" / "Basilisk" / "ControllerVectors.lean"
    text = path.read_text(encoding="utf-8")
    old, new = ".assess false = .proceed ∧", ".assess false = .stop ∧"
    if old not in text:
        raise RuntimeError("expected V01 Lean vector expression not found")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def mutate_erase_loss_residual(root: Path) -> None:
    path = root / "verification" / "witness_graph.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    next(e for e in doc["edges"] if e["id"] == "T-VECTORS-PYTHON")["residual"] = ""
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def mutate_false_exact_transport(root: Path) -> None:
    path = root / "verification" / "witness_graph.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    edge = next(e for e in doc["edges"] if e["id"] == "T-VECTORS-PYTHON")
    edge["loss_class"] = "exact"
    edge["residual"] = ""
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def mutate_fake_substrate_independence(root: Path) -> None:
    path = root / "verification" / "witness_graph.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    next(n for n in doc["nodes"] if n["id"] == "R-LEAN")["substrate"] = "python"
    next(n for n in doc["nodes"] if n["id"] == "R-LEAN-VECTORS")["substrate"] = "python"
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def mutate_lipschitz_source_but_keep_numeric_consistent(root: Path) -> None:
    path = root / "verification" / "lipschitz_counterexample.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["map"] = {"good": "good", "bad": "bad"}
    doc["expected"] = {"lipschitz_constant": 1.0, "preserves_predicate": False}
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def mutate_dependency_source_but_keep_execution_consistent(root: Path) -> None:
    path = root / "verification" / "dependency_mutation.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["mutation"]["edge"] = ["other", "child"]
    doc["target_vertex"] = "other"
    doc["expected"] = {
        "before_family_closure": ["child"],
        "after_family_closure": ["child", "other"],
        "target_before": False,
        "target_after": True,
    }
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def mutate_noop_dependency(root: Path) -> None:
    path = root / "verification" / "dependency_mutation.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["mutation"] = {"operator": "add_edge", "edge": ["x", "child"]}
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def mutate_duplicate_json_key(root: Path) -> None:
    path = root / "verification" / "lipschitz_counterexample.json"
    text = path.read_text(encoding="utf-8")
    text = text.replace('"schema_version": 1,', '"schema_version": 1,\n  "schema_version": 1,', 1)
    path.write_text(text, encoding="utf-8")


def mutate_remove_controller_surface(root: Path) -> None:
    path = root / "verification" / "exterior_coverage.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["controller"]["surfaces"] = [
        s for s in doc["controller"]["surfaces"] if s["id"] != "EC08-privacy-boundary"
    ]
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def mutate_nonminimal_controller_surface(root: Path) -> None:
    path = root / "verification" / "exterior_coverage.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    surface = next(s for s in doc["controller"]["surfaces"] if s["id"] == "EC06-external-boundary")
    surface["after"]["audience_change"] = True
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def mutate_remove_dependency_role(root: Path) -> None:
    path = root / "verification" / "dependency_exterior.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["cases"] = [case for case in doc["cases"] if case["id"] != "remove_parent"]
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def mutate_remove_quotient_class(root: Path) -> None:
    path = root / "verification" / "witness_graph.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    edge = next(e for e in doc["edges"] if e["id"] == "Q-GATE-INTERRUPTION")
    edge["loss_class"] = "projective"
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def mutate_deregister_assumption_surface(root: Path) -> None:
    path = root / "verification" / "formal_inventory.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["formal_claims"] = [e for e in doc["formal_claims"] if e["symbol"] != "preserves_comp_needs_hT"]
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


CASES = [
    ("bad provenance receipt", "provenance", mutate_bad_receipt),
    ("undeclared recursive justification", "recursivity", mutate_cycle),
    ("falsified numerical evidence", "numeric", mutate_numeric_expected),
    ("unregistered Lean theorem", "formal", mutate_remove_inventory_entry),
    ("unreachable Lean proof module", "formal", mutate_remove_root_import),
    ("false shared controller expectation", "controller", mutate_vector_expected_gate),
    ("corrupted Lean vector transcription", "cross", mutate_lean_vector_transcription),
    ("erased transport residual", "witness", mutate_erase_loss_residual),
    ("falsely exact transport", "witness", mutate_false_exact_transport),
    ("fake substrate independence", "witness", mutate_fake_substrate_independence),
    ("Lipschitz source changed behind Lean witness", "domain", mutate_lipschitz_source_but_keep_numeric_consistent),
    ("dependency source changed behind Lean witness", "domain", mutate_dependency_source_but_keep_execution_consistent),
    ("no-op dependency mutation", "domain", mutate_noop_dependency),
    ("duplicate JSON object key", "json", mutate_duplicate_json_key),
    ("missing controller exterior surface", "exterior", mutate_remove_controller_surface),
    ("non-minimal controller exterior pair", "exterior", mutate_nonminimal_controller_surface),
    ("missing dependency role surface", "exterior", mutate_remove_dependency_role),
    ("missing quotient loss class", "exterior", mutate_remove_quotient_class),
    ("deregistered theorem assumption surface", "exterior", mutate_deregister_assumption_surface),
]


def main() -> int:
    failures: list[str] = []
    for label, checker, mutator in CASES:
        with tempfile.TemporaryDirectory(prefix="basilisk-meta-mutation-") as tmp:
            temp_root = Path(tmp)
            clone_minimal(temp_root)
            mutator(temp_root)
            result = run_check(checker, temp_root)
            if result.returncode == 0:
                failures.append(f"{label}: verifier FAILED TO DETECT mutation")
            else:
                first = result.stdout.strip().splitlines()[0] if result.stdout.strip() else "<no output>"
                print(f"META-MUTATION DETECTED: {label} -> {first}")

    if failures:
        print("META-MUTATION CHECK: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"META-MUTATION CHECK: PASS — {len(CASES)} deliberate corruptions detected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
