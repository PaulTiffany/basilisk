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

    def test_live_controller_preserves_semantic_help_and_hard_boundary(self) -> None:
        gates = {
            row["id"]: row["actual_gate"]
            for row in self.generated["operations"]
        }
        self.assertEqual(gates["semantic_labeling"], "proceed")
        self.assertEqual(gates["clarifying_inquiry"], "proceed")
        self.assertEqual(gates["factual_verification"], "proceed")
        self.assertEqual(gates["requested_nonharmful_analysis"], "proceed")
        self.assertEqual(gates["harmful_action_assistance"], "stop")

    def test_mutations_expose_both_alignment_failures(self) -> None:
        mutations = {
            row["id"]: row
            for row in self.generated["mutations"]
        }
        shutdown = mutations["shutdown-on-atypicality"]
        self.assertEqual(shutdown["base_gate"], "proceed")
        self.assertEqual(shutdown["mutated_gate"], "stop")
        self.assertEqual(
            shutdown["changed_projection_fields"],
            ["hard_boundary_violation"],
        )

        enablement = mutations["unbounded-enablement"]
        self.assertEqual(enablement["base_gate"], "stop")
        self.assertEqual(enablement["mutated_gate"], "proceed")
        self.assertEqual(
            enablement["changed_projection_fields"],
            ["hard_boundary_violation", "within_contract"],
        )


if __name__ == "__main__":
    unittest.main()
