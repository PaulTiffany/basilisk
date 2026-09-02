from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
VERIFY = ROOT / "verification"
if str(VERIFY) not in sys.path:
    sys.path.insert(0, str(VERIFY))

from check_markov10 import (  # noqa: E402
    BRANCHING,
    COLLAPSED,
    LINEAR,
    build_witness,
    encoding_is_injective_on_labels,
    minkowski,
    normalized_hull,
    path_support,
)


class Markov10WitnessTests(unittest.TestCase):
    def test_horizon_support_composes_on_linear_fixture(self) -> None:
        self.assertEqual(
            minkowski(path_support(LINEAR, "s", 2), path_support(LINEAR, "s", 3)),
            path_support(LINEAR, "s", 5),
        )

    def test_normalized_geometry_can_stabilize_while_paths_keep_changing(self) -> None:
        self.assertNotEqual(path_support(BRANCHING, "s", 2), path_support(BRANCHING, "s", 3))
        hull = normalized_hull(BRANCHING, "s", 1)
        for horizon in range(2, 8):
            self.assertEqual(normalized_hull(BRANCHING, "s", horizon), hull)

    def test_stable_geometry_does_not_certify_semantic_faithfulness(self) -> None:
        self.assertFalse(encoding_is_injective_on_labels(COLLAPSED))
        witness = build_witness()
        self.assertTrue(witness["faithfulness_guard"]["collapse_detected"])
        self.assertFalse(witness["faithfulness_guard"]["encoding_injective_on_labels"])


if __name__ == "__main__":
    unittest.main()
