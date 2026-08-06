from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "PROJECT_GRAPH.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a BIS evidence manifest.")
    parser.add_argument("--output", default="bis-evidence.json")
    parser.add_argument("--verified", action="store_true")
    args = parser.parse_args()

    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    artifacts: set[str] = set(graph.get("entrypoints", {}).values())
    for layer in graph.get("layers", []):
        artifacts.update(str(path) for path in layer.get("artifacts", []))
    for principle in graph.get("principles", []):
        artifacts.update(str(path) for path in principle.get("evidence", []))

    files: list[dict[str, object]] = []
    for relative in sorted(artifacts):
        path = ROOT / relative
        if path.is_file():
            files.append(
                {
                    "path": relative,
                    "sha256": sha256(path),
                    "bytes": path.stat().st_size,
                }
            )

    evidence = {
        "schema": "basilisk-bis-evidence/v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repository": os.getenv("GITHUB_REPOSITORY"),
        "commit": os.getenv("GITHUB_SHA"),
        "ref": os.getenv("GITHUB_REF"),
        "run_id": os.getenv("GITHUB_RUN_ID"),
        "run_attempt": os.getenv("GITHUB_RUN_ATTEMPT"),
        "event_name": os.getenv("GITHUB_EVENT_NAME"),
        "verified": args.verified,
        "gate_result": os.getenv("BIS_GATE_RESULT"),
        "project_graph_sha256": sha256(GRAPH),
        "artifacts": files,
        "declared_checks": graph.get("checks", {}),
        "principles": [
            {
                "id": principle.get("id"),
                "status": principle.get("status"),
                "verified_by": principle.get("verified_by", []),
                "gaps": principle.get("gaps", []),
            }
            for principle in graph.get("principles", [])
        ],
    }

    output = ROOT / args.output
    output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote BIS evidence manifest: {output.relative_to(ROOT)} ({len(files)} artifacts)")


if __name__ == "__main__":
    main()
