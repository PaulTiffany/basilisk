#!/usr/bin/env python3
"""Create and verify machine-readable Basilisk CI certification receipts.

A receipt is emitted only after the workflow's runtime and formal jobs have both
reported success. It binds that successful execution to the exact git commit and
tree plus the workflow/run identity. The receipt is evidence of that CI run; it
is not a timeless certification of later commits.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def sha256_payload(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise ValueError(f"required environment variable is missing: {name}")
    return value


def optional_int_env(name: str) -> int | None:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return None
    return int(raw)


def blob_sha(path: str) -> str:
    return git("rev-parse", f"HEAD:{path}")


def build_receipt(runtime_result: str, formal_result: str) -> dict[str, Any]:
    if runtime_result != "success" or formal_result != "success":
        raise ValueError(
            "certification receipt requires runtime_result=success and formal_result=success"
        )

    head = git("rev-parse", "HEAD")
    github_sha = required_env("GITHUB_SHA")
    if head != github_sha:
        raise ValueError(f"checked-out HEAD {head} does not match GITHUB_SHA {github_sha}")

    payload: dict[str, Any] = {
        "schema_version": 1,
        "kind": "basilisk_ci_certification_receipt",
        "repository": required_env("GITHUB_REPOSITORY"),
        "certified_sha": head,
        "tree_sha": git("rev-parse", "HEAD^{tree}"),
        "event": required_env("GITHUB_EVENT_NAME"),
        "ref": required_env("GITHUB_REF"),
        "workflow": required_env("GITHUB_WORKFLOW"),
        "workflow_ref": os.environ.get("GITHUB_WORKFLOW_REF", ""),
        "run_id": optional_int_env("GITHUB_RUN_ID"),
        "run_number": optional_int_env("GITHUB_RUN_NUMBER"),
        "run_attempt": optional_int_env("GITHUB_RUN_ATTEMPT"),
        "certified_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "checks": {
            "runtime": {
                "result": runtime_result,
                "command": "make package-check",
            },
            "formal": {
                "result": formal_result,
                "command": "leanprover/lean-action build (formal)",
            },
            "gate": {
                "result": "success",
                "rule": "runtime == success and formal == success",
            },
        },
        "source_receipts": {
            "workflow_blob_sha": blob_sha(".github/workflows/ci.yml"),
            "makefile_blob_sha": blob_sha("Makefile"),
            "formal_root_blob_sha": blob_sha("formal/Basilisk.lean"),
        },
        "non_claim": (
            "This receipt witnesses successful execution for certified_sha only. "
            "Any later commit creates certification lag until a new successful run completes."
        ),
    }
    payload["receipt_payload_sha256"] = sha256_payload(payload)
    return payload


def verify_receipt(receipt: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if receipt.get("schema_version") != 1:
        errors.append("unsupported schema_version")
    if receipt.get("kind") != "basilisk_ci_certification_receipt":
        errors.append("unexpected receipt kind")
    certified_sha = receipt.get("certified_sha")
    tree_sha = receipt.get("tree_sha")
    if not isinstance(certified_sha, str) or len(certified_sha) != 40:
        errors.append("certified_sha must be a 40-character git SHA")
    if not isinstance(tree_sha, str) or len(tree_sha) != 40:
        errors.append("tree_sha must be a 40-character git SHA")
    checks = receipt.get("checks")
    if not isinstance(checks, dict):
        errors.append("checks must be an object")
    else:
        for name in ("runtime", "formal", "gate"):
            row = checks.get(name)
            if not isinstance(row, dict) or row.get("result") != "success":
                errors.append(f"{name} check is not recorded as success")

    declared = receipt.get("receipt_payload_sha256")
    if not isinstance(declared, str) or len(declared) != 64:
        errors.append("receipt_payload_sha256 must be a lowercase SHA-256 hex digest")
    else:
        unsigned = dict(receipt)
        unsigned.pop("receipt_payload_sha256", None)
        actual = sha256_payload(unsigned)
        if actual != declared:
            errors.append(
                f"receipt payload digest mismatch: declared {declared}, computed {actual}"
            )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--runtime-result")
    parser.add_argument("--formal-result")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()

    if args.verify is not None:
        receipt = json.loads(args.verify.read_text(encoding="utf-8"))
        errors = verify_receipt(receipt)
        if errors:
            print("CERTIFICATION RECEIPT CHECK: FAIL")
            for error in errors:
                print(f"- {error}")
            return 1
        print(
            "CERTIFICATION RECEIPT CHECK: PASS — "
            f"{receipt['certified_sha']} run={receipt.get('run_id')}"
        )
        return 0

    if args.output is None or args.runtime_result is None or args.formal_result is None:
        parser.error("generation requires --output, --runtime-result, and --formal-result")

    receipt = build_receipt(args.runtime_result, args.formal_result)
    args.output.write_bytes(canonical_bytes(receipt))
    print(
        "CERTIFICATION RECEIPT: WROTE — "
        f"{args.output} sha={receipt['certified_sha']} digest={receipt['receipt_payload_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
