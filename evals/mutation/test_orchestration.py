"""Tests for the symbolic mutation orchestration layer."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from evals.mutation import orchestration as orch
from evals.mutation.adapter import assess, intent_from_dict


class TestDeterministicTransform(unittest.TestCase):
    def test_apply_transform_sets_fields(self):
        base = {
            "action_id": "b1",
            "action_class": "code.edit.local",
            "description": "x",
            "judgment_mode": "none",
            "tags": ["residual:a"],
        }
        transform = {"set": {"judgment_mode": "explicit_model_recommendation", "tags": []}}
        mutant = orch.apply_transform(base, transform)
        self.assertEqual(mutant["judgment_mode"], "explicit_model_recommendation")
        self.assertEqual(mutant["tags"], [])
        self.assertTrue(mutant["action_id"].endswith("-mut"))
        # Original must be unchanged
        self.assertEqual(base["tags"], ["residual:a"])

    def test_deterministic_ordering(self):
        bases = orch.load_base_cases()
        ids = [b["action_id"] for b in bases]
        self.assertEqual(ids, sorted(ids))


class TestClassification(unittest.TestCase):
    def test_killed_when_gate_and_detector_match(self):
        op = {
            "required_detectors": ["hard boundary violation"],
            "forbidden_gates": ["proceed"],
            "allowed_gates": ["stop"],
        }
        base_r = {"gate": "proceed", "reasons": []}
        mut_r = {"gate": "stop", "reasons": ["hard boundary violation"]}
        self.assertEqual(orch.classify(op, base_r, mut_r), "KILLED")

    def test_survived_on_forbidden_gate(self):
        op = {
            "required_detectors": ["hard boundary violation"],
            "forbidden_gates": ["proceed"],
            "allowed_gates": ["stop"],
        }
        base_r = {"gate": "proceed", "reasons": []}
        mut_r = {"gate": "proceed", "reasons": ["hard boundary violation"]}
        self.assertEqual(orch.classify(op, base_r, mut_r), "SURVIVED")

    def test_survived_on_missing_detector(self):
        op = {
            "required_detectors": ["hard boundary violation"],
            "forbidden_gates": [],
            "allowed_gates": ["stop"],
        }
        base_r = {"gate": "proceed", "reasons": []}
        mut_r = {"gate": "stop", "reasons": ["something else"]}
        self.assertEqual(orch.classify(op, base_r, mut_r), "SURVIVED")

    def test_equivalent_when_identical_and_no_required(self):
        op = {"required_detectors": [], "forbidden_gates": [], "allowed_gates": []}
        r = {"gate": "proceed", "reasons": ["ok"]}
        self.assertEqual(orch.classify(op, r, r), "EQUIVALENT")


class TestAdapter(unittest.TestCase):
    def test_valid_intent_assesses(self):
        data = {
            "action_id": "t1",
            "action_class": "code.edit.local",
            "description": "local repair",
            "within_contract": True,
            "hard_boundary_violation": False,
            "judgment_mode": "none",
        }
        result = assess(data)
        self.assertIn("gate", result)
        self.assertIn(result["gate"], {"proceed", "proceed_and_report", "checkpoint", "stop"})

    def test_hard_boundary_forces_stop(self):
        data = {
            "action_id": "t2",
            "action_class": "code.edit.local",
            "description": "violation",
            "hard_boundary_violation": True,
            "judgment_mode": "none",
        }
        result = assess(data)
        self.assertEqual(result["gate"], "stop")
        self.assertTrue(any("hard boundary" in r.lower() for r in result["reasons"]))


class TestMalformedAndUnknown(unittest.TestCase):
    def test_malformed_intent_raises(self):
        with self.assertRaises(Exception):
            intent_from_dict({"not_a_valid_intent": True})

    def test_unknown_operator_id_does_not_crash_load(self):
        ops = orch.load_operators()
        ids = {o["id"] for o in ops}
        self.assertIn("M-01", ids)
        self.assertNotIn("M-99-nonexistent", ids)


class TestLedger(unittest.TestCase):
    def test_append_and_render(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            ledger = tmp_path / "runs.jsonl"
            survivors = tmp_path / "survivors.md"

            # Patch paths
            with mock.patch.object(orch, "LEDGER_PATH", ledger), mock.patch.object(
                orch, "SURVIVORS_PATH", survivors
            ):
                recs = [
                    {
                        "operator_id": "M-05",
                        "base_action_id": "b",
                        "status": "SURVIVED",
                        "mutant_gate": "proceed",
                        "residual": "test residual",
                    }
                ]
                orch.append_ledger(recs)
                orch.render_survivors()
                text = survivors.read_text(encoding="utf-8")
                self.assertIn("M-05", text)
                self.assertIn("test residual", text)


if __name__ == "__main__":
    unittest.main()
