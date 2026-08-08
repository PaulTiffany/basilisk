from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


GENESIS_HASH = "0" * 64
_HASH_HEX_LEN = 64
_LIST_FIELDS = ("evidence", "assumptions", "validation", "open_questions")
_REQUIRED_SERIALIZED_FIELDS = {
    "goal",
    "authority",
    "evidence",
    "assumptions",
    "action",
    "validation",
    "rollback",
    "judgment_status",
    "open_questions",
    "gate",
    "timestamp",
    "previous_hash",
    "entry_hash",
}


def _is_sha256_hex(value: str) -> bool:
    return (
        isinstance(value, str)
        and len(value) == _HASH_HEX_LEN
        and all(ch in "0123456789abcdef" for ch in value)
    )


@dataclass(frozen=True)
class LedgerEntry:
    goal: str
    authority: str
    evidence: tuple[str, ...]
    assumptions: tuple[str, ...]
    action: str
    validation: tuple[str, ...]
    rollback: str
    judgment_status: str
    open_questions: tuple[str, ...]
    gate: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    previous_hash: str = GENESIS_HASH
    entry_hash: str = ""

    def payload(self) -> dict[str, Any]:
        data = asdict(self)
        data.pop("entry_hash", None)
        data["evidence"] = list(self.evidence)
        data["assumptions"] = list(self.assumptions)
        data["validation"] = list(self.validation)
        data["open_questions"] = list(self.open_questions)
        return data

    def compute_hash(self) -> str:
        raw = json.dumps(
            self.payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    def sealed(self) -> "LedgerEntry":
        computed = self.compute_hash()
        # Serialization deliberately lowers tuple fields to JSON lists. Sealing is
        # an in-memory operation, so preserve the typed carrier rather than
        # reconstructing a LedgerEntry from its serialization representation.
        return replace(self, entry_hash=computed)

    def to_dict(self) -> dict[str, Any]:
        data = self.payload()
        data["entry_hash"] = self.entry_hash or self.compute_hash()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LedgerEntry":
        if not isinstance(data, dict):
            raise TypeError("ledger entry must be an object")
        keys = set(data)
        missing = _REQUIRED_SERIALIZED_FIELDS - keys
        extra = keys - _REQUIRED_SERIALIZED_FIELDS
        if missing:
            raise ValueError(f"ledger entry missing fields: {sorted(missing)}")
        if extra:
            raise ValueError(f"ledger entry has unknown fields: {sorted(extra)}")

        normalized = dict(data)
        for key in _LIST_FIELDS:
            value = normalized[key]
            if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                raise TypeError(f"ledger field {key!r} must be a list of strings")
            normalized[key] = tuple(value)

        for key in (
            "goal",
            "authority",
            "action",
            "rollback",
            "judgment_status",
            "gate",
            "timestamp",
            "previous_hash",
            "entry_hash",
        ):
            if not isinstance(normalized[key], str):
                raise TypeError(f"ledger field {key!r} must be a string")

        if not _is_sha256_hex(normalized["previous_hash"]):
            raise ValueError("previous_hash must be lowercase 64-character SHA-256 hex")
        if not _is_sha256_hex(normalized["entry_hash"]):
            raise ValueError("entry_hash must be lowercase 64-character SHA-256 hex")

        return cls(**normalized)


class HashLedger:
    def __init__(self, entries: Iterable[LedgerEntry] = ()) -> None:
        self._entries: list[LedgerEntry] = []
        for entry in entries:
            self._entries.append(entry)

    @property
    def entries(self) -> tuple[LedgerEntry, ...]:
        return tuple(self._entries)

    @property
    def head(self) -> str:
        if not self._entries:
            return GENESIS_HASH
        return self._entries[-1].entry_hash

    def append(self, entry: LedgerEntry) -> LedgerEntry:
        if entry.previous_hash not in {GENESIS_HASH, self.head}:
            raise ValueError("entry previous_hash does not match ledger head")
        candidate = replace(entry, previous_hash=self.head, entry_hash="").sealed()
        self._entries.append(candidate)
        return candidate

    def verify(self) -> tuple[bool, str]:
        expected_previous = GENESIS_HASH
        for index, entry in enumerate(self._entries):
            if not _is_sha256_hex(entry.previous_hash):
                return False, f"entry {index} previous_hash format invalid"
            if not _is_sha256_hex(entry.entry_hash):
                return False, f"entry {index} entry_hash format invalid"
            if entry.previous_hash != expected_previous:
                return False, f"entry {index} previous_hash mismatch"
            if entry.entry_hash != entry.compute_hash():
                return False, f"entry {index} hash mismatch"
            expected_previous = entry.entry_hash
        return True, "ok"

    def write_jsonl(self, path: str | Path) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", encoding="utf-8") as handle:
            for entry in self._entries:
                handle.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")

    @classmethod
    def read_jsonl(cls, path: str | Path) -> "HashLedger":
        entries: list[LedgerEntry] = []
        with Path(path).open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    raw = json.loads(line)
                    if not isinstance(raw, dict):
                        raise TypeError("ledger line must decode to an object")
                    entries.append(LedgerEntry.from_dict(raw))
                except (TypeError, ValueError, json.JSONDecodeError) as exc:
                    raise ValueError(f"invalid ledger line {line_number}: {exc}") from exc
        return cls(entries)
