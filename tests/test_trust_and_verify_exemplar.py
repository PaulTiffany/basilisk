from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
VERIFY = ROOT / "verification"
if str(VERIFY) not in sys.path:
    sys.path.insert(0, str(VERIFY))

from render_trust_and_verify import TARGET, build_doc, canonical_text  # noqa: E402


class TrustAndVerifyExemplarTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.generated = build_doc()
        cls.raw = TARGET.read_text(encoding="utf-8")
        cls.stored = json.loads(cls.raw)

    def test_stored_exemplar_is_exact_deterministic_render(self) -> None:
        self.assertEqual(self.stored, self.generated)
        self.assertEqual(self.raw, canonical_text(self.generated))

    def test_generated_artifact_is_observational_not_normative(self) -> None:
        self.assertEqual(self.generated["kind"], "generated_controller_observation")
        self.assertEqual(self.generated["judgment_status"], "none")
        self.assertEqual(
            self.generated["source"],
            "verification/trust_and_verify_seed.json",
        )
        serialized_seed_fields = json.dumps(self.generated)
        self.assertNotIn('"expected_gate"', serialized_seed_fields)
        self.assertNotIn('"classification"', serialized_seed_fields)
        self.assertNotIn('"required"', serialized_seed_fields)
        self.assertNotIn('"forbidden"', serialized_seed_fields)

    def test_mutations_are_observed_without_hand_authored_truth_values(self) -> None:
        for row in self.generated["mutations"]:
            self.assertTrue(row["changed_intent_fields"])
            self.assertTrue(row["changed_projection_fields"])
            self.assertIn(row["base_gate"], {"proceed", "proceed_and_report", "checkpoint", "stop"})
            self.assertIn(row["mutated_gate"], {"proceed", "proceed_and_report", "checkpoint", "stop"})


if __name__ == "__main__":
    unittest.main()
