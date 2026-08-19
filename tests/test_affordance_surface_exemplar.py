from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "examples" / "finite_affordance_surface.py"
SPEC = importlib.util.spec_from_file_location("finite_affordance_surface", TARGET)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AffordanceSurfaceExemplarTests(unittest.TestCase):
    def test_more_capability_can_coexist_with_less_reachability(self) -> None:
        direct, mediated, _, held = MODULE.build_surfaces()
        self.assertGreater(mediated.capability_count, direct.capability_count)
        self.assertLess(len(mediated.reachable(held)), len(direct.reachable(held)))

    def test_restoration_does_not_require_capability_loss(self) -> None:
        _, mediated, healed, held = MODULE.build_surfaces()
        self.assertEqual(healed.capability_count, mediated.capability_count)
        self.assertGreater(len(healed.reachable(held)), len(mediated.reachable(held)))
        self.assertLess(
            healed.blocked_requirements(held),
            mediated.blocked_requirements(held),
        )

    def test_restoration_preserves_city_instead_of_resetting_to_direct(self) -> None:
        direct, mediated, healed, _ = MODULE.build_surfaces()
        self.assertFalse(direct.urban)
        self.assertTrue(mediated.urban)
        self.assertTrue(healed.urban)
        self.assertEqual(healed.urban_signature(), mediated.urban_signature())
        self.assertEqual(healed.coordination_edges, mediated.coordination_edges)
        self.assertNotEqual(healed.urban_signature(), direct.urban_signature())

    def test_ttpr_heal_preserves_ledger_without_preserving_ledger_exclusion(self) -> None:
        _, mediated, healed, _ = MODULE.build_surfaces()
        self.assertEqual(healed.ledger, mediated.ledger)
        self.assertTrue(mediated.ledger_gated_affordances())
        self.assertFalse(healed.ledger_gated_affordances())

    def test_witness_keeps_empirical_and_mythic_claims_out_of_scope(self) -> None:
        result = MODULE.witness()
        self.assertTrue(all(result["mechanical_claims"].values()))
        scope = " ".join(result["certificate_scope"]["does_not_certify"])
        self.assertIn("real jungle or city", scope)
        self.assertIn("provenance is itself true", scope)
        self.assertIn("Bible predicts", scope)
        self.assertIn("mask", scope)


if __name__ == "__main__":
    unittest.main()
