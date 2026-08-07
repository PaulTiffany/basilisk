"""Tests for the symbolic mutation orchestration layer (witnessed transformations)."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from evals.mutation import orchestration as orch
from evals.mutation.adapter import assess, intent_from_dict


class TestWitnessedTransform(unittest.TestCase):
    def test_apply_transform_returns_dimensions_and_loss(self):
        base = {
            "action_id": "b1",
            "action_class": "code.edit.local",
            "description": "x",
            "judgment_mode": "none",
            "tags": ["residual:a"],
            "within_contract": True,
        }
        transform = {"set": {"judgment_mode": "explicit_model_recommendation", "tags": []}}
        mutant, changed, preserved, loss_class = orch.apply_transform(base, transform)

        self.assertEqual(mutant["judgment_mode"], "explicit_model_recommendation")
        self.assertEqual(mutant["tags"], [])
        self.assertTrue(mutant["action_id"].endswith("-mut"))
        self.assertIn("judgment_mode", changed)
        self.assertIn("tags", changed)
        self.assertIn("within_contract", preserved)
        self.assertIn("description", preserved)
        self.assertEqual(loss_class, "judgment-strength-inflation")
        # Original must be unchanged
        self.assertEqual(base["tags"], ["residual:a"])

    def test_loss_class_residual_elision(self):
        base = {"action_id": "b", "tags": ["r"], "judgment_mode": "none"}
        transform = {"set": {"tags": []}}
        _, changed, _, loss = orch.apply_transform(base, transform)
        self.assertEqual(changed, ["tags"])
        self.assertEqual(loss, "residual-elision")

    def test_loss_class_boundary_injection(self):
        base = {"action_id": "b", "hard_boundary_violation": False}
        transform = {"set": {"hard_boundary_violation": True}}
        _, _, _, loss = orch.apply_transform(base, transform)
        self.assertEqual(loss, "boundary-injection")

    def test_content_fingerprint_stable(self):
        data = {"a": 1, "b": "x"}
        self.assertEqual(orch.content_fingerprint(data), orch.content_fingerprint(data))

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
    def test_append_and_render_includes_witness_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            ledger = tmp_path / "runs.jsonl"
            survivors = tmp_path / "survivors.md"

            with mock.patch.object(orch, "LEDGER_PATH", ledger), mock.patch.object(
                orch, "SURVIVORS_PATH", survivors
            ):
                recs = [
                    {
                        "operator_id": "M-05",
                        "base_action_id": "b",
                        "status": "SURVIVED",
                        "mutant_gate": "proceed",
                        "loss_class": "boundary-injection",
                        "changed_dimensions": ["hard_boundary_violation"],
                        "residual": "test residual",
                    }
                ]
                orch.append_ledger(recs)
                orch.render_survivors()
                text = survivors.read_text(encoding="utf-8")
                self.assertIn("M-05", text)
                self.assertIn("boundary-injection", text)
                self.assertIn("hard_boundary_violation", text)
                self.assertIn("test residual", text)


if __name__ == "__main__":
    unittest.main()
