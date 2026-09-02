from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "evals" / "producer_authority_seed.json"
OUTPUT = ROOT / "evals" / "producer_authority.json"
SCRIPT = ROOT / "scripts" / "derive_producer_authority_exemplar.py"


class ProducerAuthorityDerivationTests(unittest.TestCase):
    def test_committed_exemplar_matches_derivation(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--check"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)

    def test_seed_and_artifact_have_expected_roles(self) -> None:
        seed = json.loads(SEED.read_text(encoding="utf-8"))
        artifact = json.loads(OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(seed["kind"], "exemplar_seed")
        self.assertEqual(artifact["kind"], "mechanical_exemplar")
        self.assertEqual(artifact["derived_from_seed"], seed["seed_id"])

    def test_certificate_refuses_wall_and_box_claims(self) -> None:
        artifact = json.loads(OUTPUT.read_text(encoding="utf-8"))
        nonclaims = " ".join(artifact["certificate_scope"]["does_not_certify"])
        self.assertIn("model is a box", nonclaims)
        self.assertIn("impermeable wall", nonclaims)


if __name__ == "__main__":
    unittest.main()
