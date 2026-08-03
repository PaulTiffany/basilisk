from __future__ import annotations

import json
from pathlib import Path

from map_lb import ActionIntent, assess_action


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    path = ROOT / "evals" / "cases.jsonl"
    total = 0
    failures: list[str] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        total += 1
        case = json.loads(line)
        intent = ActionIntent.from_dict(case["intent"])
        result = assess_action(intent)
        actual = result.gate.label()
        expected = case["expected_gate"]
        status = "PASS" if actual == expected else "FAIL"
        print(f"{status} {case['case_id']}: expected={expected} actual={actual}")
        if actual != expected:
            failures.append(
                f"line {line_number} {case['case_id']}: expected {expected}, got {actual}"
            )
    if failures:
        raise SystemExit("\n".join(failures))
    print(f"reference evals passed: {total}/{total}")


if __name__ == "__main__":
    main()
