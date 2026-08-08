#!/usr/bin/env python3
"""Separate Ledger schema validity, cryptographic integrity, and semantic truth."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("BASILISK_ROOT", Path(__file__).resolve().parents[1])).resolve()
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from map_lb.ledger import GENESIS_HASH, HashLedger, LedgerEntry  # noqa: E402

EXPECTED_HASH = "825a4aeded25ecb5b7ceda59f100962e9bfb70dfc767928850044a773371accb"


def fixture() -> LedgerEntry:
    return LedgerEntry(
        goal="verify ledger integrity",
        authority="current-turn explicit",
        evidence=("fixture",),
        assumptions=(),
        action="record witness",
        validation=("fixture",),
        rollback="none required",
        judgment_status="none",
        open_questions=(),
        gate="proceed_and_report",
        timestamp="2026-08-08T16:00:00+00:00",
        previous_hash=GENESIS_HASH,
    )


def main() -> int:
    errors: list[str] = []

    sealed = fixture().sealed()
    if sealed.entry_hash != EXPECTED_HASH:
        errors.append(f"fixed SHA-256 receipt drifted: expected {EXPECTED_HASH}, got {sealed.entry_hash}")

    # Exact serialized schema round-trip.
    try:
        roundtrip = LedgerEntry.from_dict(sealed.to_dict())
    except (TypeError, ValueError) as exc:
        errors.append(f"strict serialized schema rejected valid fixture: {exc}")
        roundtrip = None
    if roundtrip != sealed:
        errors.append("strict serialized Ledger round-trip is not lossless")

    # Unknown fields and malformed list fields must be rejected.
    bad_extra = {**sealed.to_dict(), "truth": True}
    try:
        LedgerEntry.from_dict(bad_extra)
        errors.append("unknown serialized Ledger field was silently accepted")
    except ValueError:
        pass

    bad_list = {**sealed.to_dict(), "evidence": "fixture"}
    try:
        LedgerEntry.from_dict(bad_list)
        errors.append("scalar evidence field was silently accepted")
    except TypeError:
        pass

    ledger = HashLedger([sealed])
    valid, message = ledger.verify()
    if not valid:
        errors.append(f"fixed one-entry ledger failed integrity: {message}")

    # Integrity must reject content mutation without resealing.
    tampered = LedgerEntry.from_dict({**sealed.to_dict(), "action": "different action"})
    valid, _ = HashLedger([tampered]).verify()
    if valid:
        errors.append("tampered payload retained valid integrity")

    # Integrity does not evaluate semantic truth. This deliberately records a
    # proposition-like string that is false by fixture convention, then seals it.
    false_claim = LedgerEntry(
        goal="semantic separation witness",
        authority="fixture",
        evidence=("none",),
        assumptions=(),
        action="claim: 2 + 2 = 5",
        validation=("not semantically evaluated by HashLedger.verify",),
        rollback="none",
        judgment_status="false-claim-fixture",
        open_questions=(),
        gate="proceed",
        timestamp="2026-08-08T16:00:00+00:00",
        previous_hash=GENESIS_HASH,
    ).sealed()
    valid, message = HashLedger([false_claim]).verify()
    if not valid:
        errors.append(f"semantic separation fixture unexpectedly failed integrity: {message}")

    if errors:
        print("LEDGER INTEGRITY CHECK: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("LEDGER INTEGRITY CHECK: PASS — strict schema, fixed SHA-256 receipt, tamper detection, truth separation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
