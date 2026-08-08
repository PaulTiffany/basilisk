from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


GENESIS_HASH = "0" * 64
_HASH_HEX_LEN = 64
_LIST_FIELDS = ("evidence", "assumptions", "validation", "open_questions")