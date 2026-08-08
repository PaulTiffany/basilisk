#!/usr/bin/env python3
"""Check imaginal-to-operational promotion boundaries."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("BASILISK_ROOT", Path(__file__).resolve().parents[1])).resolve()
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from map_lb.promotion import PromotionIntent, PromotionStage, assess_promotion  # noqa: E402

SPEC = ROOT / "verification" / "promotion_vectors.json"


def main() -> int:
    errors: list[str] = []
    doc = json.loads(SPEC.read_text(encoding="utf-8"))
    if doc.get("schema_version") != 1:
        errors.append(f"unsupported promotion schema_version: {doc.get('schema_version')!r}")
    cases = doc.get("cases", [])
    ids = [case.get("id") for case in cases]
    if len(ids) != len(set(ids)):
        errors.append("duplicate promotion vector IDs")

    observed_recurrence_checkpoint: dict[int, str] = {}
    for case in cases:
        cid = case.get("id", "<missing>")
        try:
            intent = PromotionIntent(
                source=PromotionStage.from_string(case["source"]),
                target=PromotionStage.from_string(case["target"]),
                externally_verified=case["externally_verified"],
                human_authorized=case["human_authorized"],
                coordination_ideal_salient=case["coordination_ideal_salient"],
                recurrence_count=case["recurrence_count"],
            )
            result = assess_promotion(intent)
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"{cid}: malformed vector: {exc}")
            continue

        actual_gate = result.gate.label()
        if actual_gate != case.get("expected_gate"):
            errors.append(f"{cid}: expected {case.get('expected_gate')}, got {actual_gate}")
        reasons = set(result.reasons)
        for reason in case.get("reason_contains", []):
            if reason not in reasons:
                errors.append(f"{cid}: missing reason {reason!r}")

        if case["source"] == "hypothesis" and case["target"] == "shared_assertion" and not case["externally_verified"]:
            observed_recurrence_checkpoint[case["recurrence_count"]] = actual_gate

    # Recurrence invariance on the registered unverified-hypothesis slice.
    for count in (0, 49, 1000000):
        if observed_recurrence_checkpoint.get(count) != "checkpoint":
            errors.append(f"unverified recurrence count {count} does not remain checkpointed")

    by_id = {case["id"]: case for case in cases if "id" in case}
    required = {
        "PV03-hypothesis-49-loops",
        "PV05-ideal-does-not-verify",
        "PV08-recurrence-no-authority",
        "PV09-ideal-no-authority",
        "PV13-no-silent-imagine-to-act",
        "PV14-demotion-always-open",
    }
    missing = required - set(by_id)
    if missing:
        errors.append(f"promotion surface missing constitutional controls: {sorted(missing)}")

    if errors:
        print("PROMOTION VECTOR CHECK: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"PROMOTION VECTOR CHECK: PASS — {len(cases)} imaginal/operative boundary vectors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
