"""Narrow adapter between the mutation harness and the reference controller.

The adapter is the only place that constructs ActionIntent objects and calls
assess_action. It never enacts authority or produces external effects.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict

# Allow import of the reference controller when run from repository root.
_SRC = Path(__file__).resolve().parents[2] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from map_lb.controller import Assessment, assess_action  # noqa: E402
from map_lb.types import ActionIntent  # noqa: E402


def intent_from_dict(data: Dict[str, Any]) -> ActionIntent:
    """Construct a frozen ActionIntent from a plain dictionary."""
    return ActionIntent.from_dict(data)


def assess(intent_data: Dict[str, Any]) -> Dict[str, Any]:
    """Run the reference controller and return a plain-dict assessment.

    Raises on construction or assessment errors so the harness can classify ERROR.
    """
    intent = intent_from_dict(intent_data)
    result: Assessment = assess_action(intent)
    return result.to_dict()
