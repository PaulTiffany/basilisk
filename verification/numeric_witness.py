#!/usr/bin/env python3
"""Deterministic NumPy witnesses for finite mathematical claims.

This is not a proof engine. It supplies independently inspectable finite examples
that should agree with the corresponding prose and Lean claims.
"""

from __future__ import annotations

import json
import numpy as np


def weighted_l1_distance_matrix(features: np.ndarray, weights: np.ndarray) -> np.ndarray:
    delta = np.abs(features[:, None, :] - features[None, :, :])
    return np.sum(delta * weights[None, None, :], axis=2)


def triangle_holds(distances: np.ndarray, atol: float = 1e-12) -> bool:
    n = distances.shape[0]
    return all(
        distances[i, k] <= distances[i, j] + distances[j, k] + atol
        for i in range(n)
        for j in range(n)
        for k in range(n)
    )


def main_data() -> dict:
    # C-MATH-004: finite witness for a weighted sum of component distances.
    weights = np.array([1.0, 2.0, 0.5], dtype=float)
    features = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 1.0],
            [1.0, 1.0, 1.0],
        ],
        dtype=float,
    )
    distances = weighted_l1_distance_matrix(features, weights)

    # Distinct underlying action IDs with identical measured features demonstrate
    # why an operational feature distance is only a pseudometric absent injectivity.
    hidden_action_ids = ["action-A", "action-B"]
    aliased_features = np.array([[1.0, 0.0], [1.0, 0.0]], dtype=float)
    alias_distance = float(
        np.sum(np.abs(aliased_features[0] - aliased_features[1]))
    )

    # C-MATH-001: constant collapse has output distance zero for every pair, hence
    # empirical Lipschitz ratio zero, while it sends the designated good state to bad.
    source = np.array([0.0, 1.0], dtype=float)
    collapsed = np.array([1.0, 1.0], dtype=float)  # both map to the `bad` point
    dx = abs(float(source[1] - source[0]))
    dy = abs(float(collapsed[1] - collapsed[0]))
    lipschitz_ratio = dy / dx
    constitutional_preserved = bool(collapsed[0] == 0.0)

    return {
        "schema_version": 1,
        "claims": {
            "C-MATH-001": {
                "source_pair_distance": dx,
                "collapsed_pair_distance": dy,
                "observed_lipschitz_ratio": lipschitz_ratio,
                "constitutional_predicate_preserved": constitutional_preserved,
            },
            "C-MATH-004": {
                "weights": weights.tolist(),
                "distance_matrix": distances.tolist(),
                "symmetric": bool(np.allclose(distances, distances.T)),
                "zero_diagonal": bool(np.allclose(np.diag(distances), 0.0)),
                "triangle_inequality_on_fixture": triangle_holds(distances),
                "alias_witness": {
                    "distinct_action_ids": hidden_action_ids[0] != hidden_action_ids[1],
                    "identical_feature_distance": alias_distance,
                },
            },
        },
    }


if __name__ == "__main__":
    print(json.dumps(main_data(), indent=2, sort_keys=True))
