from __future__ import annotations

import unittest

import _bootstrap  # noqa: F401
from map_lb import HashLedger, LedgerEntry


class LedgerTests(unittest.TestCase):
    def sample_entry(self, action: str) -> LedgerEntry:
        return LedgerEntry(
            goal="test goal",
            authority="current-turn explicit",
            evidence=("unit test",),
            assumptions=(),
            action=action,
            validation=("passed",),
            rollback="revert local diff",
            judgment_status="none",
            open_questions=(),
            gate="proceed_and_report",
            timestamp="2026-08-08T16:00:00+00:00",
        )

    def test_append_and_verify(self) -> None:
        ledger = HashLedger()
        ledger.append(self.sample_entry("first"))
        ledger.append(self.sample_entry("second"))
        valid, message = ledger.verify()
        self.assertTrue(valid, message)
        self.assertEqual(len(ledger.entries), 2)

    def test_mutation_is_detected(self) -> None:
        ledger = HashLedger()
        sealed = ledger.append(self.sample_entry("first"))
        tampered = LedgerEntry.from_dict({**sealed.to_dict(), "action": "changed"})
        compromised = HashLedger([tampered])
        valid, _ = compromised.verify()
        self.assertFalse(valid)

    def test_serialized_roundtrip_is_exact(self) -> None:
        sealed = self.sample_entry("first").sealed()
        self.assertEqual(LedgerEntry.from_dict(sealed.to_dict()), sealed)

    def test_unknown_serialized_field_is_rejected(self) -> None:
        sealed = self.sample_entry("first").sealed()
        with self.assertRaises(ValueError):
            LedgerEntry.from_dict({**sealed.to_dict(), "truth": True})

    def test_list_fields_must_be_lists_of_strings(self) -> None:
        sealed = self.sample_entry("first").sealed()
        with self.assertRaises(TypeError):
            LedgerEntry.from_dict({**sealed.to_dict(), "evidence": "unit test"})
        with self.assertRaises(TypeError):
            LedgerEntry.from_dict({**sealed.to_dict(), "evidence": [1]})

    def test_hash_representation_is_strict(self) -> None:
        sealed = self.sample_entry("first").sealed()
        with self.assertRaises(ValueError):
            LedgerEntry.from_dict({**sealed.to_dict(), "entry_hash": sealed.entry_hash.upper()})

    def test_integrity_does_not_imply_truth(self) -> None:
        false_claim = self.sample_entry("claim: 2 + 2 = 5").sealed()
        valid, message = HashLedger([false_claim]).verify()
        self.assertTrue(valid, message)


if __name__ == "__main__":
    unittest.main()
