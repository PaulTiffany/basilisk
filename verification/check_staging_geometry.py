#!/usr/bin/env python3
"""Check cumulative constraint staging as frame-indexed pseudometric refinement."""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np

from registry_io import strict_load_json

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
ROOT = Path(os.environ.get("BASILISK_ROOT", DEFAULT_ROOT)).resolve()
SPEC = ROOT / "verification" / "staging_geometry.json"


def zero_partition(ids: list[str], distances: np.ndarray) -> list[list[str]]:
    unseen = set(range(len(ids)))
    blocks: list[list[str]] = []
    while unseen:
        i = min(unseen)
        block_idx = [j for j in range(len(ids)) if distances[i, j] == 0.0]
        for j in block_idx:
            unseen.discard(j)
        blocks.append([ids[j] for j in block_idx])
    return blocks


def main() -> int:
    doc = strict_load_json(SPEC)
    errors: list[str] = []
    if not isinstance(doc, dict) or doc.get("schema_version") != 1:
        errors.append("staging geometry registry must be a schema_version 1 object")
        print("STAGING GEOMETRY CHECK: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    states = doc.get("states", [])
    weights_raw = doc.get("weights", [])
    stages = doc.get("stages", [])
    if not isinstance(states, list) or not states:
        errors.append("states must be a nonempty list")
        states = []
    if not isinstance(weights_raw, list) or not weights_raw:
        errors.append("weights must be a nonempty list")
        weights_raw = []
    if not isinstance(stages, list) or not stages:
        errors.append("stages must be a nonempty list")
        stages = []

    if errors:
        print("STAGING GEOMETRY CHECK: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    ids = [str(state["id"]) for state in states]
    features = np.asarray([state["features"] for state in states], dtype=float)
    weights = np.asarray(weights_raw, dtype=float)
    if features.ndim != 2 or features.shape[1] != len(weights):
        errors.append("feature dimension must match weights")
    if np.any(weights < 0):
        errors.append("weights must be nonnegative")

    previous: np.ndarray | None = None
    previous_active: list[int] = []
    strict_refinement = False

    for expected_k, stage in enumerate(stages, start=1):
        k = stage.get("k")
        active = stage.get("active_components")
        scale = stage.get("frame_scale")
        if k != expected_k:
            errors.append(f"stage position {expected_k}: expected k={expected_k}, got {k!r}")
        if active != list(range(expected_k)):
            errors.append(f"stage {k}: active components must be exact prefix {list(range(expected_k))}")
            continue
        if previous_active and active[: len(previous_active)] != previous_active:
            errors.append(f"stage {k}: activation is not prefix-monotone")
        previous_active = list(active)
        if type(scale) not in (int, float) or scale <= 0:
            errors.append(f"stage {k}: frame_scale must be positive")
            continue

        delta = np.abs(features[:, None, active] - features[None, :, active])
        distances = np.sum(delta * weights[active][None, None, :], axis=2)
        partition = zero_partition(ids, distances)
        expected_partition = stage.get("expected_zero_partition")
        if partition != expected_partition:
            errors.append(f"stage {k}: zero partition expected {expected_partition!r}, got {partition!r}")

        scaled = distances * float(scale)
        if not np.array_equal(distances == 0.0, scaled == 0.0):
            errors.append(f"stage {k}: positive frame scaling changed the zero kernel")

        if previous is not None:
            if np.any(distances < previous):
                errors.append(f"stage {k}: cumulative distance decreased pointwise")
            prev_zero = previous == 0.0
            now_zero = distances == 0.0
            if np.any(now_zero & ~prev_zero):
                errors.append(f"stage {k}: zero kernel enlarged instead of refining")
            if np.any(prev_zero & ~now_zero):
                strict_refinement = True
        previous = distances

    if not strict_refinement:
        errors.append("registered fixture lacks a strict zero-kernel refinement")

    if errors:
        print("STAGING GEOMETRY CHECK: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "STAGING GEOMETRY CHECK: PASS — "
        f"{len(stages)} frame-indexed stages, pointwise monotonicity, "
        "zero-kernel refinement, and positive-scale invariance"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
