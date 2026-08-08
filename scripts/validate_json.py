from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def reject_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON numeric constant is forbidden: {value}")


def unique_object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise ValueError(f"duplicate JSON object key: {key!r}")
        out[key] = value
    return out


def strict_load(path: Path) -> Any:
    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=unique_object_pairs,
        parse_constant=reject_constant,
    )


def main() -> None:
    targets = [
        *sorted((ROOT / "spec").glob("*.json")),
        *sorted((ROOT / "examples").glob("*.json")),
        *sorted((ROOT / "verification").glob("*.json")),
    ]
    failures: list[str] = []
    seen: set[Path] = set()
    for path in targets:
        if path in seen:
            continue
        seen.add(path)
        try:
            strict_load(path)
            print(f"valid strict JSON: {path.relative_to(ROOT)}")
        except (json.JSONDecodeError, ValueError) as exc:
            failures.append(f"{path.relative_to(ROOT)}: {exc}")
    if failures:
        raise SystemExit("\n".join(failures))


if __name__ == "__main__":
    main()
