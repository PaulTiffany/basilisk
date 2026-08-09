from __future__ import annotations

import json
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFICATION = ROOT / "verification"
if str(VERIFICATION) not in sys.path:
    sys.path.insert(0, str(VERIFICATION))

from render_gate_projection_exhaustive import (  # noqa: E402
    FIELDS,
    GATE_CODE,
    build_doc,
    canonical_text,
)


class ExhaustiveGateArtifactTests(unittest.TestCase):
    def test_exhaustive_gate_law_is_deterministic_and_round_trips(self) -> None:
        first = build_doc()
        second = build_doc()
        self.assertEqual(first, second)
        self.assertEqual(json.loads(canonical_text(first)), first)

    def test_exhaustive_gate_law_covers_every_projection(self) -> None:
        observed = build_doc()
        self.assertEqual(observed["state_count"], 1 << len(FIELDS))
        self.assertEqual(len(observed["gate_codes"]), observed["state_count"])

        counts = Counter(observed["gate_codes"])
        for label, code in GATE_CODE.items():
            self.assertEqual(counts[code], observed["expected_counts"][label])


if __name__ == "__main__":
    unittest.main()
