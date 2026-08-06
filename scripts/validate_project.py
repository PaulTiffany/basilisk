from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
GRAPH_PATH = ROOT / "PROJECT_GRAPH.json"
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
ALLOWED_STATUSES = {"declared", "partial", "implemented"}


def resolve_local_link(source: Path, raw_target: str) -> Path | None:
    target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
    parsed = urlparse(target)
    if parsed.scheme or target.startswith(("#", "mailto:")):
        return None
    path_text = unquote(parsed.path)
    if not path_text:
        return None
    return ROOT / path_text.lstrip("/") if path_text.startswith("/") else source.parent / path_text


def validate_markdown_links(failures: list[str]) -> None:
    for source in sorted(ROOT.rglob("*.md")):
        if ".git" in source.parts:
            continue
        text = source.read_text(encoding="utf-8")
        for match in MARKDOWN_LINK.finditer(text):
            target = resolve_local_link(source, match.group(1))
            if target is not None and not target.resolve().exists():
                failures.append(
                    f"broken markdown link: {source.relative_to(ROOT)} -> {match.group(1)}"
                )


def validate_layers(graph: dict[str, object], failures: list[str]) -> None:
    layers = graph.get("layers", [])
    if not isinstance(layers, list):
        failures.append("PROJECT_GRAPH.json: layers must be a list")
        return

    by_id: dict[str, dict[str, object]] = {}
    for layer in layers:
        if not isinstance(layer, dict):
            failures.append("PROJECT_GRAPH.json: every layer must be an object")
            continue
        layer_id = layer.get("id")
        if not isinstance(layer_id, str) or not layer_id:
            failures.append("PROJECT_GRAPH.json: every layer needs a non-empty id")
            continue
        if layer_id in by_id:
            failures.append(f"duplicate layer id: {layer_id}")
        by_id[layer_id] = layer
        for artifact in layer.get("artifacts", []):
            if not (ROOT / str(artifact)).exists():
                failures.append(f"missing layer artifact: {layer_id} -> {artifact}")

    for layer_id, layer in by_id.items():
        for dependency in layer.get("depends_on", []):
            if dependency not in by_id:
                failures.append(f"unknown layer dependency: {layer_id} -> {dependency}")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(layer_id: str) -> None:
        if layer_id in visited:
            return
        if layer_id in visiting:
            failures.append(f"cycle in layer dependency graph at: {layer_id}")
            return
        visiting.add(layer_id)
        for dependency in by_id[layer_id].get("depends_on", []):
            if dependency in by_id:
                visit(str(dependency))
        visiting.remove(layer_id)
        visited.add(layer_id)

    for layer_id in by_id:
        visit(layer_id)


def validate_cross_links(graph: dict[str, object], failures: list[str]) -> None:
    for binding in graph.get("cross_links", []):
        if not isinstance(binding, dict):
            failures.append("PROJECT_GRAPH.json: cross_links entries must be objects")
            continue
        source = ROOT / str(binding.get("source", ""))
        target_name = str(binding.get("target", ""))
        target = ROOT / target_name
        if not source.exists():
            failures.append(f"cross-link source is missing: {source.relative_to(ROOT)}")
            continue
        if not target.exists():
            failures.append(f"cross-link target is missing: {target.relative_to(ROOT)}")
            continue
        if target_name not in source.read_text(encoding="utf-8"):
            failures.append(
                f"declared cross-link absent: {source.relative_to(ROOT)} -> {target_name}"
            )


def validate_principles(graph: dict[str, object], failures: list[str]) -> None:
    philosophy = (ROOT / "PHILOSOPHY.md").read_text(encoding="utf-8")
    checks = graph.get("checks", {})
    check_ids = set(checks) if isinstance(checks, dict) else set()
    seen: set[str] = set()

    for principle in graph.get("principles", []):
        if not isinstance(principle, dict):
            failures.append("PROJECT_GRAPH.json: principles entries must be objects")
            continue
        principle_id = str(principle.get("id", ""))
        phrase = str(principle.get("phrase", ""))
        status = str(principle.get("status", ""))
        if not principle_id or principle_id in seen:
            failures.append(f"missing or duplicate principle id: {principle_id!r}")
        seen.add(principle_id)
        if not phrase or phrase not in philosophy:
            failures.append(
                f"principle phrase absent from PHILOSOPHY.md: {principle_id} {phrase!r}"
            )
        if status not in ALLOWED_STATUSES:
            failures.append(f"invalid principle status: {principle_id} -> {status!r}")
        evidence = principle.get("evidence", [])
        if not evidence:
            failures.append(f"principle has no evidence bindings: {principle_id}")
        for artifact in evidence:
            if not (ROOT / str(artifact)).exists():
                failures.append(f"missing principle evidence: {principle_id} -> {artifact}")
        for check_id in principle.get("verified_by", []):
            if check_id not in check_ids:
                failures.append(f"unknown verification check: {principle_id} -> {check_id}")
        if status != "implemented" and not principle.get("gaps"):
            failures.append(f"non-implemented principle must state gaps: {principle_id}")


def validate_workflow(graph: dict[str, object], failures: list[str]) -> None:
    workflow = graph.get("workflow", {})
    if not isinstance(workflow, dict):
        failures.append("PROJECT_GRAPH.json: workflow must be an object")
        return
    path = ROOT / str(workflow.get("path", ""))
    if not path.exists():
        failures.append(f"declared workflow is missing: {path.relative_to(ROOT)}")
        return
    text = path.read_text(encoding="utf-8")
    for snippet in workflow.get("required_snippets", []):
        if str(snippet) not in text:
            failures.append(f"workflow orchestration snippet missing: {snippet}")


def main() -> None:
    failures: list[str] = []
    try:
        graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"cannot load PROJECT_GRAPH.json: {exc}") from exc

    for label, artifact in graph.get("entrypoints", {}).items():
        if not (ROOT / str(artifact)).exists():
            failures.append(f"missing entrypoint: {label} -> {artifact}")

    validate_markdown_links(failures)
    validate_layers(graph, failures)
    validate_cross_links(graph, failures)
    validate_principles(graph, failures)
    validate_workflow(graph, failures)

    if failures:
        raise SystemExit("project orchestration validation failed:\n- " + "\n- ".join(failures))

    print(
        "project orchestration valid: "
        f"{len(graph.get('layers', []))} layers, "
        f"{len(graph.get('principles', []))} principles, "
        f"{len(graph.get('cross_links', []))} required cross-links"
    )


if __name__ == "__main__":
    main()
