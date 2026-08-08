"""Strict, deterministic loading for verification registry JSON.

Verification registries are executable evidence. They therefore use stricter
loading rules than ordinary convenience JSON:
- duplicate object keys are rejected;
- NaN/Infinity-style constants are rejected;
- shard names are explicit rather than broad globs;
- schema and payload container types are checked before callers consume them.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


_SHARD_SUFFIX = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON numeric constant is forbidden: {value}")


def _unique_object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise ValueError(f"duplicate JSON object key: {key!r}")
        out[key] = value
    return out


def strict_load_json(path: Path) -> Any:
    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=_unique_object_pairs,
        parse_constant=_reject_constant,
    )


def discover_registry_shards(
    directory: Path,
    *,
    base_name: str,
    shard_prefix: str,
    errors: list[str],
) -> list[Path]:
    """Return deterministic registry shards and reject ambiguous lookalikes.

    Allowed names are exactly ``base_name`` or
    ``<shard_prefix><safe-suffix>.json``. A file such as ``bindings-old.json``
    or ``bindings_backup.json.bak`` must never silently become registry state.
    """

    base = directory / base_name
    broad_stem = Path(base_name).stem
    candidates = sorted(directory.glob(f"{broad_stem}*.json"))
    allowed: list[Path] = []

    for path in candidates:
        if path.name == base_name:
            allowed.append(path)
            continue
        if path.name.startswith(shard_prefix) and path.suffix == ".json":
            suffix = path.stem[len(shard_prefix) :]
            if suffix and _SHARD_SUFFIX.fullmatch(suffix):
                allowed.append(path)
                continue
        errors.append(f"ambiguous registry lookalike is not an allowed shard: {path.name}")

    if not base.is_file():
        errors.append(f"required base registry missing: {base_name}")
    if not allowed:
        errors.append(f"no registry shards found for {base_name}")
    return sorted(allowed, key=lambda path: path.name)


def load_registry_list(
    directory: Path,
    *,
    base_name: str,
    shard_prefix: str,
    payload_key: str,
    errors: list[str],
) -> tuple[list[dict[str, Any]], list[str]]:
    """Load and validate a list-valued registry across deterministic shards."""

    paths = discover_registry_shards(
        directory,
        base_name=base_name,
        shard_prefix=shard_prefix,
        errors=errors,
    )
    items: list[dict[str, Any]] = []
    names: list[str] = []

    for path in paths:
        names.append(path.name)
        try:
            doc = strict_load_json(path)
        except (json.JSONDecodeError, ValueError) as exc:
            errors.append(f"{path.name}: malformed strict JSON: {exc}")
            continue
        if not isinstance(doc, dict):
            errors.append(f"{path.name}: registry root must be an object")
            continue
        version = doc.get("schema_version")
        if type(version) is not int or version != 1:
            errors.append(f"{path.name}: unsupported schema_version {version!r}")
        payload = doc.get(payload_key)
        if not isinstance(payload, list):
            errors.append(f"{path.name}: {payload_key} must be a list")
            continue
        for index, item in enumerate(payload):
            if not isinstance(item, dict):
                errors.append(f"{path.name}: {payload_key}[{index}] must be an object")
                continue
            items.append(item)

    return items, names
