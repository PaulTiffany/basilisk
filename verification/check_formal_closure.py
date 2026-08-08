#!/usr/bin/env python3
"""Check closure of the local Lean theorem inventory."""

from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path

from registry_io import load_registry_list, strict_load_json

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
ROOT = Path(os.environ.get("BASILISK_ROOT", DEFAULT_ROOT)).resolve()
FORMAL_DIR = ROOT / "formal" / "Basilisk"
ROOT_KERNEL = ROOT / "formal" / "Basilisk.lean"
CLAIMS = ROOT / "verification" / "claims.json"

DECL_START = re.compile(r"^(theorem|lemma)\s+([A-Za-z0-9_'.]+)")
IMPORT = re.compile(r"^import\s+Basilisk\.([A-Za-z0-9_'.]+)\s*$")


def normalize(text: str) -> str:
    return " ".join(text.split())


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def strip_lean_comments(text: str) -> str:
    """Remove Lean line/block comments while preserving line structure.

    Lean block comments may nest. String contents are preserved so comment-like
    text in declarations does not accidentally alter parsing.
    """
    out: list[str] = []
    i = 0
    block_depth = 0
    in_string = False
    escaped = False
    while i < len(text):
        if block_depth:
            if text.startswith("/-", i):
                block_depth += 1
                out.extend("  ")
                i += 2
            elif text.startswith("-/", i):
                block_depth -= 1
                out.extend("  ")
                i += 2
            else:
                out.append("\n" if text[i] == "\n" else " ")
                i += 1
            continue

        ch = text[i]
        if in_string:
            out.append(ch)
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            i += 1
            continue

        if ch == '"':
            in_string = True
            out.append(ch)
            i += 1
        elif text.startswith("/-", i):
            block_depth = 1
            out.extend("  ")
            i += 2
        elif text.startswith("--", i):
            out.extend("  ")
            i += 2
            while i < len(text) and text[i] != "\n":
                out.append(" ")
                i += 1
        else:
            out.append(ch)
            i += 1
    if block_depth:
        raise ValueError("unterminated Lean block comment")
    return "".join(out)


def extract_declarations(path: Path) -> list[dict]:
    try:
        cleaned = strip_lean_comments(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise ValueError(f"{path}: {exc}") from exc
    lines = cleaned.splitlines()
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
                raise ValueError(f"declaration {symbol} in {path} reached another declaration before :=")
            parts.append(nxt)
            terminated = ":=" in nxt
        joined = " ".join(parts)
        signature = normalize(joined.split(":=", 1)[0].rstrip())
        out.append({"kind": kind, "symbol": symbol, "signature": signature, "statement_sha256": sha256(signature)})
        i = j + 1
    return out


def module_name(path: Path) -> str:
    return path.stem


def load_inventory_entries(errors: list[str]) -> tuple[list[dict], list[str]]:
    return load_registry_list(ROOT / "verification", base_name="formal_inventory.json", shard_prefix="formal_inventory_", payload_key="formal_claims", errors=errors)


def main() -> int:
    errors: list[str] = []
    entries, inventory_names = load_inventory_entries(errors)
    try:
        claims_doc = strict_load_json(CLAIMS)
    except Exception as exc:
        print("FORMAL CLOSURE CHECK: FAIL")
        print(f"- claims.json: malformed strict JSON: {exc}")
        return 1
    if not isinstance(claims_doc, dict):
        print("FORMAL CLOSURE CHECK: FAIL")
        print("- claims.json root must be an object")
        return 1
    raw_claims = claims_doc.get("claims", [])
    if not isinstance(raw_claims, list):
        errors.append("claims.json: claims must be a list")
        raw_claims = []
    semantic_ids = {c["id"] for c in raw_claims if isinstance(c, dict) and "id" in c}
    ids = [e.get("id") for e in entries]
    if len(ids) != len(set(ids)):
        errors.append("duplicate formal inventory IDs across shards")
    symbols = [e.get("symbol") for e in entries]
    if len(symbols) != len(set(symbols)):
        errors.append("duplicate formal theorem symbols across inventory shards")
    by_key = {(e.get("module"), e.get("symbol")): e for e in entries}
    discovered: dict[tuple[str, str], dict] = {}
    module_files = sorted(p for p in FORMAL_DIR.glob("*.lean") if p.name != "Basilisk.lean")
    for path in module_files:
        rel = path.relative_to(ROOT).as_posix()
        try:
            declarations = extract_declarations(path)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        for declaration in declarations:
            key = (rel, declaration["symbol"])
            if key in discovered:
                errors.append(f"duplicate discovered Lean declaration: {declaration['symbol']} in {rel}")
            discovered[key] = declaration
            if key not in by_key:
                errors.append(f"unregistered Lean {declaration['kind']}: {declaration['symbol']} in {rel}")
    for key, entry in by_key.items():
        module, symbol = key
        if not isinstance(module, str) or not isinstance(symbol, str):
            errors.append(f"inventory entry missing string module/symbol: {entry!r}")
            continue
        actual = discovered.get(key)
        if actual is None:
            errors.append(f"inventory entry has no live declaration: {symbol} in {module}")
            continue
        registered_signature = normalize(str(entry.get("signature", "")))
        if registered_signature != actual["signature"]:
            errors.append(f"statement drift for {symbol}: registered signature no longer matches source")
        registered_sha = entry.get("statement_sha256", "")
        if registered_sha != actual["statement_sha256"]:
            errors.append(f"statement receipt drift for {symbol}: expected {registered_sha}, computed {actual['statement_sha256']}")
        semantic = entry.get("semantic_claim_id")
        if semantic is not None and semantic not in semantic_ids:
            errors.append(f"{symbol}: unknown semantic_claim_id {semantic}")
        deps = entry.get("semantic_depends_on", [])
        if not isinstance(deps, list):
            errors.append(f"{symbol}: semantic_depends_on must be a list")
            deps = []
        for dep in deps:
            if dep not in semantic_ids:
                errors.append(f"{symbol}: unknown semantic dependency {dep}")
    imports = set()
    for line in ROOT_KERNEL.read_text(encoding="utf-8").splitlines():
        match = IMPORT.match(line.strip())
        if match:
            imports.add(match.group(1))
    modules_with_proofs = {module_name(ROOT / module) for (module, _symbol) in discovered}
    for module in sorted(modules_with_proofs):
        if module not in imports:
            errors.append(f"formal module containing local proofs is not imported by root kernel: Basilisk.{module}")
    linked_semantic = {e.get("semantic_claim_id") for e in entries if e.get("semantic_claim_id")}
    for claim in raw_claims:
        if isinstance(claim, dict) and claim.get("status") == "lean_theorem" and claim.get("id") not in linked_semantic:
            errors.append(f"semantic Lean claim lacks formal-inventory linkage: {claim.get('id')}")
    if errors:
        print("FORMAL CLOSURE CHECK: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"FORMAL CLOSURE CHECK: PASS — {len(discovered)} local theorem/lemma declarations, {len(imports)} root imports, {len(inventory_names)} inventory shard(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
