#!/usr/bin/env python3
"""Report CI certification freshness for the current Basilisk main head.

The most recent successful *push* run of `.github/workflows/ci.yml` on `main` is
treated as the last certified commit because that workflow's merge-gate requires
both `make package-check` and the Lean build to succeed.

This script deliberately distinguishes workflow success from current freshness:
a successful run for an ancestor is green-but-stale, not fresh green.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

DEFAULT_REPOSITORY = "PaulTiffany/basilisk"
DEFAULT_WORKFLOW = "ci.yml"


@dataclass(frozen=True)
class CompareResult:
    status: str
    ahead_by: int
    behind_by: int


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def api_json(repository: str, path: str) -> Any:
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    request = urllib.request.Request(
        f"https://api.github.com/repos/{repository}/{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "basilisk-certification-status/1",
            **({"Authorization": f"Bearer {token}"} if token else {}),
        },
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def current_main_sha(repository: str) -> str:
    try:
        return git("rev-parse", "HEAD")
    except (subprocess.CalledProcessError, FileNotFoundError):
        commit = api_json(repository, "commits/main")
        return str(commit["sha"])


def latest_successful_push(repository: str, workflow: str) -> dict[str, Any] | None:
    query = urllib.parse.urlencode(
        {
            "branch": "main",
            "event": "push",
            "status": "success",
            "per_page": 100,
        }
    )
    doc = api_json(repository, f"actions/workflows/{workflow}/runs?{query}")
    runs = doc.get("workflow_runs", [])
    if not isinstance(runs, list) or not runs:
        return None
    # API returns newest first for this endpoint; still sort defensively by run_number.
    runs = [r for r in runs if isinstance(r, dict) and r.get("conclusion") == "success"]
    if not runs:
        return None
    runs.sort(key=lambda row: int(row.get("run_number", 0)), reverse=True)
    return runs[0]


def compare(repository: str, certified_sha: str, head_sha: str) -> CompareResult:
    doc = api_json(repository, f"compare/{certified_sha}...{head_sha}")
    return CompareResult(
        status=str(doc.get("status", "unknown")),
        ahead_by=int(doc.get("ahead_by", 0)),
        behind_by=int(doc.get("behind_by", 0)),
    )


def status_payload(repository: str, workflow: str) -> dict[str, Any]:
    head = current_main_sha(repository)
    run = latest_successful_push(repository, workflow)
    if run is None:
        return {
            "schema_version": 1,
            "repository": repository,
            "workflow": workflow,
            "head_sha": head,
            "certification_state": "unknown",
            "reason": "no successful main/push workflow run found",
        }

    certified = str(run["head_sha"])
    cmp = compare(repository, certified, head)
    if certified == head:
        state = "fresh"
        lag = 0
    elif cmp.status == "ahead":
        state = "lagging"
        lag = cmp.ahead_by
    elif cmp.status == "behind":
        state = "certified_ahead_of_checked_head"
        lag = None
    elif cmp.status == "diverged":
        state = "diverged"
        lag = None
    else:
        state = "unknown"
        lag = None

    return {
        "schema_version": 1,
        "repository": repository,
        "workflow": workflow,
        "head_sha": head,
        "certification_state": state,
        "lag_commits": lag,
        "last_certified_sha": certified,
        "last_certified_run_id": run.get("id"),
        "last_certified_run_number": run.get("run_number"),
        "last_certified_run_attempt": run.get("run_attempt"),
        "last_certified_created_at": run.get("created_at"),
        "last_certified_updated_at": run.get("updated_at"),
        "last_certified_html_url": run.get("html_url"),
        "compare": {
            "status": cmp.status,
            "ahead_by": cmp.ahead_by,
            "behind_by": cmp.behind_by,
        },
        "fresh_definition": (
            "fresh iff current head SHA equals the head SHA of the most recent successful "
            "main/push run of the configured workflow"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", DEFAULT_REPOSITORY))
    parser.add_argument("--workflow", default=DEFAULT_WORKFLOW)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--require-fresh", action="store_true")
    args = parser.parse_args()

    try:
        payload = status_payload(args.repository, args.workflow)
    except (urllib.error.URLError, urllib.error.HTTPError, KeyError, ValueError) as exc:
        payload = {
            "schema_version": 1,
            "repository": args.repository,
            "workflow": args.workflow,
            "certification_state": "unknown",
            "reason": str(exc),
        }

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        state = payload.get("certification_state", "unknown")
        if state == "fresh":
            print(
                "CERTIFICATION STATUS: FRESH GREEN — "
                f"{payload.get('head_sha')} run={payload.get('last_certified_run_id')} lag=0"
            )
        elif state == "lagging":
            print(
                "CERTIFICATION STATUS: GREEN BUT STALE — "
                f"certified={payload.get('last_certified_sha')} head={payload.get('head_sha')} "
                f"lag={payload.get('lag_commits')} commit(s)"
            )
        else:
            print(
                "CERTIFICATION STATUS: "
                f"{str(state).upper()} — {payload.get('reason', payload.get('compare', ''))}"
            )

    return 0 if (not args.require_fresh or payload.get("certification_state") == "fresh") else 1


if __name__ == "__main__":
    raise SystemExit(main())
