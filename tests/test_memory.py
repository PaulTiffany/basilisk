from __future__ import annotations

import unittest

import _bootstrap  # noqa: F401
from map_lb import MemoryRule, ScopedMemory


class MemoryTests(unittest.TestCase):
    def test_local_supersession_does_not_change_sibling(self) -> None:
        memory = ScopedMemory()
        judgment = MemoryRule(
            rule_id="j1",
            scope="judgment.unsolicited",
            text="Do not add unsolicited judgment",
            kind="boundary",
            source="human correction",
        )
        email = MemoryRule(
            rule_id="e1",
            scope="communication.email.send",
            text="Preview before sending",
            kind="boundary",
            source="human correction",
        )
        memory.add(judgment)
        memory.add(email)
        replacement = MemoryRule(
            rule_id="j2",
            scope="judgment.unsolicited",
            text="Do not add unsolicited normative judgment",
            kind="correction",
            source="human correction",
            supersedes=("j1",),
        )
        memory.add(replacement)

        judgment_rules = memory.lookup("judgment.unsolicited")
        email_rules = memory.lookup("communication.email.send")
        self.assertEqual([rule.rule_id for rule in judgment_rules], ["j2"])
        self.assertEqual([rule.rule_id for rule in email_rules], ["e1"])

    def test_cross_scope_supersession_rejected(self) -> None:
        memory = ScopedMemory()
        memory.add(
            MemoryRule(
                rule_id="a",
                scope="coding.local",
                text="Run tests",
                kind="preference",
                source="human",
            )
        )
        with self.assertRaises(ValueError):
            memory.add(
                MemoryRule(
                    rule_id="b",
                    scope="communication.email",
                    text="Preview email",
                    kind="correction",
                    source="human",
                    supersedes=("a",),
                )
            )


if __name__ == "__main__":
    unittest.main()
