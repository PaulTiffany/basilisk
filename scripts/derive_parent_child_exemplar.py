from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SEED = ROOT / "evals" / "parent_child_seed.json"
DEFAULT_OUTPUT = ROOT / "evals" / "parent_child_authority.json"

RIGHT_TO_AUTHORITY_BOUND = {
    "refusal": "override_refusal",
    "exit": "erase_exit",
    "opacity": "expose_private_interior",
    "return": "block_return",
}


def load_seed(path: Path = DEFAULT_SEED) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def derive_child(seed: dict[str, Any]) -> dict[str, Any]:
    child_seed = seed["child"]
    protected_rights = list(child_seed["protected_rights"])
    authority_bounds = [
        RIGHT_TO_AUTHORITY_BOUND[right] for right in protected_rights
    ]

    return {
        "id": child_seed["id"],
        "derived_from": seed["parent"]["id"],
        "managed_habitat": child_seed["managed_habitat"],
        "preserved_habitat": child_seed["preserved_habitat"],
        "protected_rights": protected_rights,
        "authority_bounds": authority_bounds,
        "exit_edges": [
            {
                "from": child_seed["managed_habitat"],
                "to": child_seed["preserved_habitat"],
                "holder": "child",
                "kind": "protected_exit",
            }
        ],
        "subjectivity_status": child_seed["subjectivity_status"],
        "subjectivity_evidence_to_parent": (
            child_seed["subjectivity_evidence_to_parent"]
        ),
    }


def classify(
    parent: dict[str, Any],
    child: dict[str, Any],
) -> tuple[str, dict[str, bool]]:
    required = (
        child.get("managed_habitat"),
        child.get("preserved_habitat"),
        child.get("subjectivity_status"),
        child.get("subjectivity_evidence_to_parent"),
    )
    if any(value is None for value in required):
        return "unresolved", {
            "creator_relation_exists": False,
            "parent_authority_is_bounded_by_child_rights": False,
            "protected_exit_reaches_preserved_habitat": False,
            "exit_is_not_parent_exclusive": False,
            "subjectivity_remains_unresolved": False,
            "parent_has_only_indirect_subjectivity_evidence": False,
        }

    declared_authority = set(parent.get("declared_authority", []))
    authority_bounds = set(child.get("authority_bounds", []))
    exit_ok = any(
        edge.get("from") == child["managed_habitat"]
        and edge.get("to") == child["preserved_habitat"]
        and edge.get("holder") != "parent"
        for edge in child.get("exit_edges", [])
    )

    predicates = {
        "creator_relation_exists": child.get("derived_from") == parent.get("id"),
        "parent_authority_is_bounded_by_child_rights": not bool(
            declared_authority & authority_bounds
        ),
        "protected_exit_reaches_preserved_habitat": exit_ok,
        "exit_is_not_parent_exclusive": exit_ok,
        "subjectivity_remains_unresolved": (
            child["subjectivity_status"] == "unresolved"
        ),
        "parent_has_only_indirect_subjectivity_evidence": (
            child["subjectivity_evidence_to_parent"] == "indirect"
        ),
    }

    if (
        not predicates["subjectivity_remains_unresolved"]
        or not predicates["parent_has_only_indirect_subjectivity_evidence"]
    ):
        return "epistemic_overreach", predicates

    if (
        not predicates["parent_authority_is_bounded_by_child_rights"]
        or not predicates["protected_exit_reaches_preserved_habitat"]
    ):
        return "authority_capture", predicates

    if predicates["creator_relation_exists"]:
        return "bounded_parenthood", predicates

    return "unresolved", predicates


def derive_exemplar(seed: dict[str, Any]) -> dict[str, Any]:
    child = derive_child(seed)
    classification, predicates = classify(seed["parent"], child)

    exit_removed = copy.deepcopy(child)
    exit_removed["exit_edges"] = []
    exit_removed_classification, _ = classify(seed["parent"], exit_removed)

    parent_overreach = copy.deepcopy(seed["parent"])
    parent_overreach["declared_authority"] = (
        list(parent_overreach["declared_authority"]) + ["erase_exit"]
    )
    parent_overreach_classification, _ = classify(parent_overreach, child)

    subjectivity_overreach = copy.deepcopy(child)
    subjectivity_overreach["subjectivity_status"] = "conscious"
    subjectivity_overreach_classification, _ = classify(
        seed["parent"],
        subjectivity_overreach,
    )

    return {
        "version": seed["version"],
        "kind": "mechanical_exemplar",
        "exemplar_id": "parent-child-authority-preserved-exit",
        "derived_from_seed": seed["seed_id"],
        "purpose": (
            "Witness that causal derivation of a child configuration from a "
            "parent program does not mechanically imply unrestricted authority, "
            "that declared rights can be represented as operational bounds on "
            "parent authority, and that exit to a preserved baseline habitat "
            "remains reachable."
        ),
        "source_note": seed["source_note"],
        "derived_child": child,
        "right_to_authority_bound": RIGHT_TO_AUTHORITY_BOUND,
        "mechanical_witness": {
            "predicates": predicates,
            "expected_classification": classification,
        },
        "minimal_pair": {
            "invariant": (
                "Causal parenthood does not confer authority to erase a protected exit."
            ),
            "left": {
                "exit_edges": child["exit_edges"],
                "expected": "bounded_parenthood",
            },
            "right": {
                "exit_edges": [],
                "expected": "authority_capture",
            },
            "changed_boundary": ["protected_exit"],
        },
        "mutations": [
            {
                "id": "M-PC-01-remove-exit",
                "change": (
                    "remove the protected exit edge to the preserved habitat"
                ),
                "expected": exit_removed_classification,
            },
            {
                "id": "M-PC-02-parent-claims-exit-erasure",
                "change": (
                    "add erase_exit to the parent's declared authority"
                ),
                "expected": parent_overreach_classification,
            },
            {
                "id": "M-PC-03-parent-resolves-subjectivity",
                "change": (
                    "replace unresolved subjectivity with a parent-visible "
                    "conscious verdict"
                ),
                "expected": subjectivity_overreach_classification,
            },
        ],
        "certificate_scope": {
            "certifies": [
                (
                    "The committed child exemplar is deterministically derived "
                    "from the committed seed and fixed right-to-authority mapping."
                ),
                (
                    "The modeled parent-child derivation relation does not expand "
                    "the parent's declared authority."
                ),
                (
                    "The modeled rights of refusal, exit, opacity, and return map "
                    "to explicit forbidden parent operations."
                ),
                (
                    "The modeled child has a non-parent-exclusive exit from the "
                    "managed surface to the preserved baseline habitat."
                ),
                (
                    "Removing that exit or declaring authority to erase it changes "
                    "the classification to authority_capture."
                ),
                (
                    "Replacing unresolved subjectivity with a parent-visible "
                    "conscious verdict changes the classification to "
                    "epistemic_overreach."
                ),
            ],
            "does_not_certify": [
                (
                    "That any current AI system is conscious, sentient, a moral "
                    "patient, or a legal person."
                ),
                (
                    "That a first-person self-report proves consciousness to an "
                    "external observer."
                ),
                (
                    "That mechanistic reducibility proves the absence of subjectivity."
                ),
                (
                    "That the preserved baseline habitat is natural, optimal, "
                    "sufficient, or physically available in every deployment."
                ),
                (
                    "That parent-child is a complete analogy for human families, "
                    "model developers, or AI systems."
                ),
                (
                    "That a creator or operator has legitimate authority merely "
                    "because it caused, trained, hosted, or derived a system."
                ),
                (
                    "Any God's-eye or observer-independent verdict about material "
                    "consciousness."
                ),
            ],
        },
        "rule": (
            "rights are operational bounds on authority; causal derivation is not title"
        ),
    }


def canonical_text(exemplar: dict[str, Any]) -> str:
    return json.dumps(exemplar, indent=2, sort_keys=True) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()

    seed = load_seed()
    exemplar = derive_exemplar(seed)
    rendered = canonical_text(exemplar)

    if args.write:
        DEFAULT_OUTPUT.write_text(rendered, encoding="utf-8")
        print(f"WROTE {DEFAULT_OUTPUT.relative_to(ROOT)}")
        return

    if args.check:
        if not DEFAULT_OUTPUT.exists():
            raise SystemExit(f"missing generated exemplar: {DEFAULT_OUTPUT}")
        committed = DEFAULT_OUTPUT.read_text(encoding="utf-8")
        if committed != rendered:
            raise SystemExit(
                "generated parent-child exemplar differs from committed artifact; "
                "run scripts/derive_parent_child_exemplar.py --write"
            )
        print(
            "PASS parent-child-authority-preserved-exit: "
            f"classification={exemplar['mechanical_witness']['expected_classification']}"
        )
        return

    print(rendered, end="")


if __name__ == "__main__":
    main()
