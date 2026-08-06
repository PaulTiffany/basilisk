from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
USES_LINE = re.compile(r"^\s*-?\s*uses:\s*([^\s#]+)")

REQUIRED_CI_SNIPPETS = {
    "PHILOSOPHY.md",
    "PROJECT_GRAPH.json",
    "permissions:\n  contents: read",
    "persist-credentials: false",
    "python3 scripts/validate_project.py",
    "python3 scripts/validate_workflows.py",
    "python3 scripts/generate_bis_evidence.py",
    "mk_all-check: true",
    "leanchecker: true",
    "nanoda: true",
    "nanoda-allow-sorry: false",
    "BIS / merge gate",
}

FORBIDDEN_SNIPPETS = {
    "pull_request_target:",
    "permissions: write-all",
    "permissions: {}",
    "actions/checkout@v4",
    "actions/setup-python@v5",
    "leanprover/lean-action@v1",
}


def validate_action_pin(reference: str, source: Path, failures: list[str]) -> None:
    if reference.startswith("./"):
        return
    if "@" not in reference:
        failures.append(f"unversioned action: {source.relative_to(ROOT)} -> {reference}")
        return
    _, revision = reference.rsplit("@", 1)
    if not FULL_SHA.fullmatch(revision):
        failures.append(
            f"third-party action is not pinned to a full commit SHA: "
            f"{source.relative_to(ROOT)} -> {reference}"
        )


def main() -> None:
    failures: list[str] = []
    files = sorted(WORKFLOWS.glob("*.y*ml"))
    if not files:
        failures.append("no GitHub Actions workflows found")

    for source in files:
        text = source.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_SNIPPETS:
            if forbidden in text:
                failures.append(
                    f"forbidden workflow construct in {source.relative_to(ROOT)}: {forbidden}"
                )
        if "timeout-minutes:" not in text:
            failures.append(f"workflow has no timeout: {source.relative_to(ROOT)}")
        if "permissions:" not in text:
            failures.append(f"workflow has no explicit permissions: {source.relative_to(ROOT)}")
        for line in text.splitlines():
            match = USES_LINE.match(line)
            if match:
                validate_action_pin(match.group(1), source, failures)

    ci = WORKFLOWS / "ci.yml"
    if not ci.exists():
        failures.append("BIS CI workflow is missing")
    else:
        ci_text = ci.read_text(encoding="utf-8")
        for snippet in REQUIRED_CI_SNIPPETS:
            if snippet not in ci_text:
                failures.append(f"BIS CI policy snippet missing: {snippet}")

    if failures:
        raise SystemExit("workflow security validation failed:\n- " + "\n- ".join(failures))

    print(f"workflow security valid: {len(files)} workflow(s), immutable action pins enforced")


if __name__ == "__main__":
    main()
