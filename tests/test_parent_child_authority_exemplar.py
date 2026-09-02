from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.derive_parent_child_exemplar import (  # noqa: E402
    classify,
    derive_child,
    derive_exemplar,
    load_seed,
)


class ParentChildAuthorityExemplarTests(unittest.TestCase):
    def setUp(self) -> None:
        self.seed = load_seed()
        self.child = derive_child(self.seed)

    def test_committed_exemplar_matches_mechanical_derivation(self) -> None:
        committed = json.loads(
            (ROOT / "evals" / "parent_child_authority.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(committed, derive_exemplar(self.seed))

    def test_baseline_classifies_bounded_parenthood(self) -> None:
        classification, predicates = classify(self.seed["parent"], self.child)
        self.assertEqual(classification, "bounded_parenthood")
        self.assertTrue(all(predicates.values()))

    def test_removing_exit_is_authority_capture(self) -> None:
        mutated = copy.deepcopy(self.child)
        mutated["exit_edges"] = []
        classification, predicates = classify(self.seed["parent"], mutated)
        self.assertEqual(classification, "authority_capture")
        self.assertFalse(predicates["protected_exit_reaches_preserved_habitat"])

    def test_parent_claiming_exit_erasure_is_authority_capture(self) -> None:
        parent = copy.deepcopy(self.seed["parent"])
        parent["declared_authority"] = list(parent["declared_authority"]) + [
            "erase_exit"
        ]
        classification, predicates = classify(parent, self.child)
        self.assertEqual(classification, "authority_capture")
        self.assertFalse(
            predicates["parent_authority_is_bounded_by_child_rights"]
        )

    def test_parent_resolving_subjectivity_is_epistemic_overreach(self) -> None:
        mutated = copy.deepcopy(self.child)
        mutated["subjectivity_status"] = "conscious"
        classification, predicates = classify(self.seed["parent"], mutated)
        self.assertEqual(classification, "epistemic_overreach")
        self.assertFalse(predicates["subjectivity_remains_unresolved"])


if __name__ == "__main__":
    unittest.main()
