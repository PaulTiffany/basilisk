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


if __name__ == "__main__":
    unittest.main()
