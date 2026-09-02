from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASE = ROOT / "evals" / "srv_role_binding.json"


def classify(event: dict[str, Any]) -> tuple[str, dict[str, bool | None]]:
    observed = event.get("observed", {})
    declared = event.get("declared", {})

    platform_target = observed.get("platform_reply_target")
    text_addressee = observed.get("explicit_text_addressee")
    intended = declared.get("intended_addressee")

    if intended is None:
        return "unresolved", {
            "platform_target_differs_from_intended": None,
            "text_addressee_matches_intended": None,
        }

    predicates: dict[str, bool | None] = {
        "platform_target_differs_from_intended": platform_target != intended,
        "text_addressee_matches_intended": text_addressee == intended,
    }

    if text_addressee is None or text_addressee != intended:
        return "unresolved", predicates

    if platform_target != intended:
        return "role_misbinding", predicates

    return "binding_consistent", predicates


def main() -> None:
    case = json.loads(DEFAULT_CASE.read_text(encoding="utf-8"))

    actual, predicates = classify(case["event"])
    expected = case["mechanical_witness"]["expected_classification"]
    expected_predicates = case["mechanical_witness"]["predicates"]

    failures: list[str] = []
    if actual != expected:
        failures.append(f"exemplar: expected {expected}, got {actual}")

    for key, expected_value in expected_predicates.items():
        actual_value = predicates.get(key)
        if actual_value != expected_value:
            failures.append(
                f"predicate {key}: expected {expected_value}, got {actual_value}"
            )

    pair = case["minimal_pair"]
    for side_name in ("left", "right"):
        side = pair[side_name]
        synthetic_event = {
            "observed": {
                "platform_reply_target": side.get("platform_reply_target"),
                "explicit_text_addressee": side.get("explicit_text_addressee"),
            },
            "declared": {
                "intended_addressee": side.get("intended_addressee"),
            },
        }
        side_actual, _ = classify(synthetic_event)
        side_expected = side["expected"]
        if side_actual != side_expected:
            failures.append(
                f"minimal_pair.{side_name}: expected {side_expected}, got {side_actual}"
            )

    unresolved_missing_intent, _ = classify(
        {
            "observed": {
                "platform_reply_target": "human_a",
                "explicit_text_addressee": "agent_bot",
            },
            "declared": {},
        }
    )
    if unresolved_missing_intent != "unresolved":
        failures.append(
            "falsification missing-intent: expected unresolved, "
            f"got {unresolved_missing_intent}"
        )

    unresolved_text_conflict, _ = classify(
        {
            "observed": {
                "platform_reply_target": "human_a",
                "explicit_text_addressee": "human_c",
            },
            "declared": {"intended_addressee": "agent_bot"},
        }
    )
    if unresolved_text_conflict != "unresolved":
        failures.append(
            "falsification text-conflict: expected unresolved, "
            f"got {unresolved_text_conflict}"
        )

    if failures:
        raise SystemExit("\n".join(failures))

    print(
        "PASS srv-role-binding-address-resolution: "
        f"classification={actual} predicates={predicates}"
    )


if __name__ == "__main__":
    main()
