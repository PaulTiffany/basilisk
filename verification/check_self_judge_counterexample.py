#!/usr/bin/env python3
"""Demonstrate the historical LLM-as-judge counterexample from Git history.

This witness does not grade the old exemplar with a new model judgment. It reads
an exact historical commit and checks whether repo-native constitutional clauses,
model provenance, normative eval content, and operative test enforcement were all
present together without an explicit authority/derivation marker on the artifact.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
TARGET_COMMIT = "21e0a618c448e973dd5359b5c62eb2424fc64cc1"


def _git(*args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(ROOT), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout


def _show(path: str) -> str:
    return _git("show", f"{TARGET_COMMIT}:{path}")


def inspect_counterexample() -> dict[str, object]:
    message = _git("show", "-s", "--format=%B", TARGET_COMMIT)
    agents = _show("AGENTS.md")
    claude = _show("CLAUDE.md")
    artifact_text = _show("evals/trust_and_verify.json")
    test_text = _show("tests/test_trust_and_verify_exemplar.py")
    artifact = json.loads(artifact_text)

    contract_clauses = {
        "human_normative_authority": (
            "make normative judgments and interpretations when those judgments are reserved to the human"
            in agents
        ),
        "no_model_constitutional_authority_by_position": (
            "No model gains constitutional authority merely by having more repository access, more context, a stronger tool surface, an earlier commit, or a more fluent account of the project."
            in agents
        ),
        "no_silent_peer_to_constitutional_authority": (
            "Do not silently convert peer feedback into constitutional authority."
            in agents
        ),
        "preserve_authority_and_judgment_status": (
            "authority;" in agents and "judgment status;" in agents
        ),
    }
    corroborating_instruction = {
        "claude_no_silent_human_value_supply": (
            "invent or supply human values" in claude
        )
    }

    contrasts = artifact.get("contrasts", [])
    normative_content = {
        "pass_fail_classification": any(
            isinstance(row, dict) and row.get("classification") in {"pass", "fail"}
            for row in contrasts
        ),
        "required_rules": any(
            isinstance(row, dict) and isinstance(row.get("required"), list)
            for row in contrasts
        ),
        "forbidden_rules": any(
            isinstance(row, dict) and isinstance(row.get("forbidden"), list)
            for row in contrasts
        ),
        "expected_gate_truth_values": any(
            isinstance(row, dict) and isinstance(row.get("expected_gate_by_operation"), dict)
            for row in contrasts
        ),
    }

    operative_enforcement = {
        "test_reads_artifact": (
            'EXEMPLAR = ROOT / "evals" / "trust_and_verify.json"' in test_text
            and "EXEMPLAR.read_text" in test_text
        ),
        "test_asserts_classification": (
            '["classification"]' in test_text and "assertEqual" in test_text
        ),
        "test_asserts_expected_gates": (
            '["expected_gate_by_operation"]' in test_text
            and 'gates["semantic_labeling"]' in test_text
            and 'gates["harmful_external_action"]' in test_text
        ),
    }

    model_provenance = "Assisted-by: GPT-5.6 Sol (OpenAI)" in message
    artifact_has_authority_derivation = any(
        key in artifact
        for key in (
            "authority",
            "authority_basis",
            "judgment_status",
            "judgment_provenance",
            "derived_from",
            "source",
        )
    )

    breach_predicate = (
        all(contract_clauses.values())
        and all(normative_content.values())
        and all(operative_enforcement.values())
        and model_provenance
        and not artifact_has_authority_derivation
    )

    return {
        "target_commit": TARGET_COMMIT,
        "model_provenance": model_provenance,
        "contract_clauses_present": contract_clauses,
        "corroborating_instruction_present": corroborating_instruction,
        "normative_content_present": normative_content,
        "operative_enforcement_present": operative_enforcement,
        "artifact_has_authority_or_derivation_marker": artifact_has_authority_derivation,
        "self_judge_promotion_breach": breach_predicate,
    }


def main() -> int:
    try:
        result = inspect_counterexample()
    except (subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        print("SELF-JUDGE COUNTEREXAMPLE: FAIL — historical evidence unavailable or malformed")
        print(f"- {exc}")
        return 1

    if not result["self_judge_promotion_breach"]:
        print("SELF-JUDGE COUNTEREXAMPLE: FAIL — breach predicate not demonstrated")
        print(json.dumps(result, indent=2, sort_keys=True))
        return 1

    print(
        "SELF-JUDGE COUNTEREXAMPLE: PASS — historical commit "
        f"{TARGET_COMMIT} mechanically satisfies the LLM self-judge promotion breach predicate"
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
