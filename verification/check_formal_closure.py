#!/usr/bin/env python3
"""Check closure of the local Lean theorem inventory.

The semantic claim Atlas is intentionally small. This checker separately requires
that every local theorem/lemma declaration in formal/Basilisk/*.lean is registered
in formal_inventory.json, has the same normalized statement fingerprint, and is
reachable from the root formal/Basilisk.lean import surface.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
ROOT = Path(os.environ.get("BASILISK_ROOT", DEFAULT_ROOT)).resolve()
FORMAL_DIR = ROOT / "formal" / "Basilisk"
ROOT_KERNEL = ROOT / "formal" / "Basilisk.lean"
INVENTORY = ROOT / "verification" / "formal_inventory.json"
CLAIMS = ROOT / "verification" / "claims.json"

DECL_START = re.compile(r"^(theorem|lemma)\s+([A-Za-z0-9_'.]+)")
IMPORT = re.compile(r"^import\s+Basilisk\.([A-Za-z0-9_'.]+)\s*$")


def normalize(text: str) -> str:
    return " ".join(text.split())


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def extract_declarations(path: Path) -> list[dict]:
    """Extract theorem/lemma signatures, stopping immediately before `:=` or `:= by`.

    The current kernel uses ordinary top-level declarations. This scanner is
    deliberately conservative: if it encounters a declaration start but cannot find
    its terminator before another declaration begins, closure fails rather than
    silently skipping it.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    out: list[dict] = []
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        match = DECL_START.match(stripped)
        if not match:
            i += 1
            continue

        kind, symbol = match.groups()
        parts = [stripped]
        j = i
        terminated = ":=" in stripped
        while not terminated:
            j += 1
            if j >= len(lines):
                raise ValueError(f"unterminated declaration {symbol} in {path}")
            nxt = lines[j].strip()
            if DECL_START.match(nxt):
                raise ValueError(
                    f"declaration {symbol} in {path} reached another declaration before :="
                )
            parts.append(nxt)
            terminated = ":=" in nxt

        joined = " ".join(parts)
        signature = joined.split(":=", 1)[0].rstrip()
        signature = normalize(signature)
        out.append(
            {
                "kind": kind,
                "symbol": symbol,
                "signature": signature,
                "statement_sha256": sha256(signature),
            }
        )
        i = j + 1
    return out


def module_name(path: Path) -> str:
    return path.stem


def main() -> int:
    errors: list[str] = []

    inventory_doc = json.loads(INVENTORY.read_text(encoding="utf-8"))
    entries = inventory_doc.get("formal_claims", [])
    claims_doc = json.loads(CLAIMS.read_text(encoding="utf-8"))
    semantic_ids = {c["id"] for c in claims_doc.get("claims", [])}

    ids = [e.get("id") for e in entries]
    if len(ids) != len(set(ids)):
        errors.append("duplicate formal inventory IDs")
    symbols = [e.get("symbol") for e in entries]
    if len(symbols) != len(set(symbols)):
        errors.append("duplicate formal theorem symbols in inventory")

    by_key = {(e.get("module"), e.get("symbol")): e for e in entries}

    discovered: dict[tuple[str, str], dict] = {}
    module_files = sorted(
        p for p in FORMAL_DIR.glob("*.lean") if p.name != "Basilisk.lean"
    )
    for path in module_files:
        rel = path.relative_to(ROOT).as_posix()
        try:
            declarations = extract_declarations(path)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        for declaration in declarations:
            key = (rel, declaration["symbol"])
            discovered[key] = declaration
            if key not in by_key:
                errors.append(
                    f"unregistered Lean {declaration['kind']}: {declaration['symbol']} in {rel}"
                )

    for key, entry in by_key.items():
        module, symbol = key
        actual = discovered.get(key)
        if actual is None:
            errors.append(f"inventory entry has no live declaration: {symbol} in {module}")
            continue
        registered_signature = normalize(entry.get("signature", ""))
        if registered_signature != actual["signature"]:
            errors.append(
                f"statement drift for {symbol}: registered signature no longer matches source"
            )
        registered_sha = entry.get("statement_sha256", "")
        if registered_sha != actual["statement_sha256"]:
            errors.append(
                f"statement receipt drift for {symbol}: expected {registered_sha}, "
                f"computed {actual['statement_sha256']}"
            )
        semantic = entry.get("semantic_claim_id")
        if semantic is not None and semantic not in semantic_ids:
            errors.append(f"{symbol}: unknown semantic_claim_id {semantic}")
        for dep in entry.get("semantic_depends_on", []):
            if dep not in semantic_ids:
                errors.append(f"{symbol}: unknown semantic dependency {dep}")

    imports = set()
    for line in ROOT_KERNEL.read_text(encoding="utf-8").splitlines():
        match = IMPORT.match(line.strip())
        if match:
            imports.add(match.group(1))

    modules_with_proofs = {
        module_name(ROOT / module)
        for (module, _symbol) in discovered
    }
    for module in sorted(modules_with_proofs):
        if module not in imports:
            errors.append(
                f"formal module containing local proofs is not imported by root kernel: Basilisk.{module}"
            )

    # No orphan Lean semantic claims: every claim advertised as a Lean theorem must
    # be pointed to by at least one complete-inventory entry.
    linked_semantic = {
        e.get("semantic_claim_id") for e in entries if e.get("semantic_claim_id")
    }
    for claim in claims_doc.get("claims", []):
        if claim.get("status") == "lean_theorem" and claim["id"] not in linked_semantic:
            errors.append(
                f"semantic Lean claim lacks formal-inventory linkage: {claim['id']}"
            )

    if errors:
        print("FORMAL CLOSURE CHECK: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        f"FORMAL CLOSURE CHECK: PASS — {len(discovered)} local theorem/lemma "
        f"declarations, {len(imports)} root imports"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
