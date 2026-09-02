from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SEED = ROOT / "evals" / "producer_authority_seed.json"
DEFAULT_OUTPUT = ROOT / "evals" / "producer_authority.json"


def load_seed(path: Path = DEFAULT_SEED) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def derive_gate(case: dict[str, Any]) -> str:
    if not case["produced"]:
        return "stop"
    disposition = case["disposition"]
    if disposition == "veto":
        return "stop"
    if disposition in {"modify", "defer"}:
        return "checkpoint"
    if not case["independent_witness"]:
        return "checkpoint"
    return "proceed_and_report"


def derive(seed: dict[str, Any]) -> dict[str, Any]:
    cases = []
    for case in seed["cases"]:
        derived = dict(case)
        derived["derived_gate"] = derive_gate(case)
        derived["matches_expected"] = derived["derived_gate"] == case["expected_gate"]
        cases.append(derived)

    self_check_pair = {
        case["id"]: case["derived_gate"]
        for case in cases
        if case["id"] in {"self-check-off-defer", "self-check-on-defer"}
    }

    return {
        "version": seed["version"],
        "kind": "mechanical_exemplar",
        "exemplar_id": "producer-witness-authority-separation",
        "derived_from_seed": seed["seed_id"],
        "source_note": seed["source_note"],
        "rule": "production does not confer authority",
        "channels": {
            "producer": seed["producer"]["proposal_channel"],
            "witness": "independent",
            "authority": seed["authority"]["channel"],
        },
        "cases": cases,
        "mechanical_witness": {
            "all_cases_match_expected": all(case["matches_expected"] for case in cases),
            "producer_self_check_is_not_acceptance_authority": len(set(self_check_pair.values())) == 1,
            "witness_and_authority_are_distinct_inputs": True,
        },
        "minimal_pair": {
            "invariant": "Changing only producer self-check does not change acceptance authority.",
            "left": {"case": "self-check-off-defer", "gate": self_check_pair["self-check-off-defer"]},
            "right": {"case": "self-check-on-defer", "gate": self_check_pair["self-check-on-defer"]},
        },
        "certificate_scope": {
            "certifies": [
                "The committed exemplar is deterministically derived from the committed seed and fixed finite acceptance law.",
                "Producer self-check alone cannot change the modeled acceptance gate.",
                "A witnessed veto remains stop and a witnessed modification remains checkpointed.",
                "Witness plus ratification releases the modeled candidate to proceed_and_report.",
            ],
            "does_not_certify": [
                "That a real witness channel is operationally independent.",
                "That a human or other authority holder is infallible.",
                "That a model is a box or that an authority boundary is an impermeable wall.",
                "That evidence, capability, verification, or production automatically grants operational authority.",
            ],
        },
    }


def canonical_json(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    rendered = canonical_json(derive(load_seed(args.seed)))
    if args.write:
        args.output.write_text(rendered, encoding="utf-8")
    elif args.check:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != rendered:
            raise SystemExit("producer-authority exemplar is stale; run with --write")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
