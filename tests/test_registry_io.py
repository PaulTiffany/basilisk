from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFICATION = ROOT / "verification"
if str(VERIFICATION) not in sys.path:
    sys.path.insert(0, str(VERIFICATION))

from registry_io import discover_registry_shards, load_registry_list, strict_load_json


class StrictJsonTests(unittest.TestCase):
    def test_duplicate_keys_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.json"
            path.write_text('{"a": 1, "a": 2}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate JSON object key"):
                strict_load_json(path)

    def test_nonstandard_constants_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.json"
            path.write_text('{"x": NaN}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "non-standard JSON numeric constant"):
                strict_load_json(path)


class RegistryShardTests(unittest.TestCase):
    def _write(self, directory: Path, name: str, text: str) -> None:
        (directory / name).write_text(text, encoding="utf-8")

    def test_base_and_named_shards_are_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            self._write(directory, "bindings.json", '{"schema_version":1,"bindings":[]}')
            self._write(directory, "bindings_zeta.json", '{"schema_version":1,"bindings":[]}')
            self._write(directory, "bindings_alpha.json", '{"schema_version":1,"bindings":[]}')
            errors: list[str] = []
            paths = discover_registry_shards(
                directory,
                base_name="bindings.json",
                shard_prefix="bindings_",
                errors=errors,
            )
            self.assertEqual(errors, [])
            self.assertEqual(
                [path.name for path in paths],
                ["bindings.json", "bindings_alpha.json", "bindings_zeta.json"],
            )

    def test_ambiguous_lookalike_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            self._write(directory, "bindings.json", '{"schema_version":1,"bindings":[]}')
            self._write(directory, "bindings-old.json", '{"schema_version":1,"bindings":[]}')
            errors: list[str] = []
            discover_registry_shards(
                directory,
                base_name="bindings.json",
                shard_prefix="bindings_",
                errors=errors,
            )
            self.assertTrue(any("ambiguous registry lookalike" in error for error in errors))

    def test_missing_base_registry_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            self._write(directory, "bindings_extra.json", '{"schema_version":1,"bindings":[]}')
            errors: list[str] = []
            discover_registry_shards(
                directory,
                base_name="bindings.json",
                shard_prefix="bindings_",
                errors=errors,
            )
            self.assertTrue(any("required base registry missing" in error for error in errors))

    def test_payload_must_be_list_of_objects(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            self._write(directory, "bindings.json", '{"schema_version":1,"bindings":{}}')
            errors: list[str] = []
            items, _ = load_registry_list(
                directory,
                base_name="bindings.json",
                shard_prefix="bindings_",
                payload_key="bindings",
                errors=errors,
            )
            self.assertEqual(items, [])
            self.assertTrue(any("bindings must be a list" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
