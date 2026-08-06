from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    targets = [
        ROOT / "PROJECT_GRAPH.json",
        *sorted((ROOT / "spec").glob("*.json")),
        *sorted((ROOT / "examples").glob("*.json")),
    ]
    failures: list[str] = []
    for path in targets:
        try:
            json.loads(path.read_text(encoding="utf-8"))
            print(f"valid JSON: {path.relative_to(ROOT)}")
        except json.JSONDecodeError as exc:
            failures.append(f"{path}: {exc}")
    if failures:
        raise SystemExit("\n".join(failures))


if __name__ == "__main__":
    main()
