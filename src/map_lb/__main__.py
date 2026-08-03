from __future__ import annotations

import argparse
import json
from pathlib import Path

from .controller import assess_action
from .ledger import HashLedger
from .types import ActionIntent, RiskLevel, StandingAuthority


def _load_json(path: str) -> dict[str, object]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def command_assess(args: argparse.Namespace) -> int:
    intent = ActionIntent.from_dict(_load_json(args.intent))
    authority = None
    if args.authority:
        raw = _load_json(args.authority)
        authority = StandingAuthority(
            authority_id=str(raw["authority_id"]),
            allowed_actions=tuple(raw["allowed_actions"]),
            max_scope=RiskLevel[str(raw.get("max_scope", "moderate")).upper()],
            allow_external_write=bool(raw.get("allow_external_write", False)),
            allow_audience_change=bool(raw.get("allow_audience_change", False)),
            allow_privacy_change=bool(raw.get("allow_privacy_change", False)),
            allow_authority_expansion=bool(
                raw.get("allow_authority_expansion", False)
            ),
            active=bool(raw.get("active", True)),
            expires_at=raw.get("expires_at"),
            notes=str(raw.get("notes", "")),
        )
    result = assess_action(intent, authority)
    print(json.dumps(result.to_dict(), indent=2))
    return 0


def command_verify_ledger(args: argparse.Namespace) -> int:
    ledger = HashLedger.read_jsonl(args.path)
    valid, message = ledger.verify()
    print(json.dumps({"valid": valid, "message": message, "head": ledger.head}, indent=2))
    return 0 if valid else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="map-lb")
    subparsers = parser.add_subparsers(dest="command", required=True)

    assess = subparsers.add_parser("assess", help="assess one action intent JSON file")
    assess.add_argument("intent")
    assess.add_argument("--authority")
    assess.set_defaults(func=command_assess)

    verify = subparsers.add_parser("verify-ledger", help="verify a JSONL ledger")
    verify.add_argument("path")
    verify.set_defaults(func=command_verify_ledger)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
