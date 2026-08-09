from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFICATION = ROOT / "verification"
if str(VERIFICATION) not in sys.path:
    sys.path.insert(0, str(VERIFICATION))

from generate_gate_projection_exhaustive import canonical_document  # noqa: E402


class ExhaustiveGateArtifactTests(unittest.TestCase):
    def test_stored_artifact_is_valid_json(self) -> None:
        path = VERIFICATION / "gate_projection_exhaustive.json"
        with path.open("r", encoding="utf-8") as handle:
            observed = json.load(handle)
        self.assertIsInstance(observed, dict)

    def test_stored_artifact_exactly_matches_live_gate_law(self) -> None:
        path = VERIFICATION / "gate_projection_exhaustive.json"
        with path.open("r", encoding="utf-8") as handle:
            observed = json.load(handle)
        self.assertEqual(observed, canonical_document())


if __name__ == "__main__":
    unittest.main()
