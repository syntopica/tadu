"""The published JSON schema of a task file names exactly the keys tadu reads and writes."""

import json
from pathlib import Path

from tadu.kinds import KINDS
from tadu.task_key_order import TASK_KEY_ORDER
from tadu.task_value_checks import TASK_VALUE_CHECKS

SCHEMA = Path(__file__).resolve().parent.parent / "spec" / "task.v2.schema.json"


def test_the_schema_and_the_code_know_the_same_keys_in_the_same_order() -> None:
    properties = json.loads(SCHEMA.read_text())["properties"]
    assert tuple(properties) == TASK_KEY_ORDER
    assert set(TASK_VALUE_CHECKS) == set(TASK_KEY_ORDER)
    assert tuple(properties["kind"]["enum"]) == KINDS
    assert properties["check_on"]["$ref"] == "#/$defs/date"
