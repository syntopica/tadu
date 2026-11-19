"""The validators and the published JSON Schemas accept exactly the same files.

spec/task.v2.schema.json and spec/config.v2.schema.json are the contract other tools
read; tadu checks by hand, which is 40x faster than jsonschema and words its findings for
people. Here jsonschema is the referee, on files hypothesis derives from real ones.
"""

import copy
import json
from pathlib import Path

import jsonschema
from hypothesis import given
from hypothesis import strategies as st

from tadu.task_problems import task_problems
from tadu.todo_config_problems import todo_config_problems

ROOT = Path(__file__).parent.parent
TASK_SCHEMA = json.loads((ROOT / "spec" / "task.v2.schema.json").read_text())
CONFIG_SCHEMA = json.loads((ROOT / "spec" / "config.v2.schema.json").read_text())
TASKS = [json.loads(p.read_text()) for p in sorted((ROOT / "todo").glob("*/*.json"))]
CONFIG = json.loads((ROOT / "todo" / "tadu.json").read_text())
VALUES: st.SearchStrategy[object] = st.sampled_from(
    [
        None,
        True,
        0,
        1,
        -1,
        1.5,
        "",
        " ",
        "x",
        "x" * 201,
        [],
        {},
        ["ok"],
        ["Bad Label"],
        [""],
        [1],
        "2026-02-30",
        "2026-1-5",
        "2026-01-05",
        "t-123",
        "t-00000000-0000-4000-8000-000000000000",
        "done",
        "cancelled",
        "blocked",
        "urgent",
        "agent:x",
        "Ana Smith",
        "http://x",
        "no uri",
        "a\nb",
        "ok-slug",
        "Bad_Slug",
        "3h",
        "3x",
        {"bug": "Bug"},
        {"Bad Key": "x"},
        {"ok": ""},
        {"by": "month"},
        {"v1": {"title": "Launch"}},
        {"v1": {"due": "2026-02-30"}},
    ]
)


def mutated(base: dict[str, object], keys: list[str]) -> st.SearchStrategy[dict[str, object]]:
    change: st.SearchStrategy[tuple[str, object, bool]] = st.tuples(
        st.sampled_from(keys), st.one_of(st.just(None), VALUES), st.booleans()
    )

    def apply(changes: list[tuple[str, object, bool]]) -> dict[str, object]:
        result = copy.deepcopy(base)
        for key, value, drop in changes:
            if drop:
                result.pop(key, None)
            else:
                result[key] = copy.deepcopy(value)
        return result

    return st.lists(change, max_size=3).map(apply)


TASK_KEYS = sorted({*TASK_SCHEMA["properties"], "x-team", "unknown"})
CONFIG_KEYS = sorted({*CONFIG_SCHEMA["properties"], "x-team", "unknown"})


@given(st.sampled_from(TASKS).flatmap(lambda task: mutated(task, TASK_KEYS)))
def test_tasks(task: dict[str, object]) -> None:  # type: ignore[misc]  # hypothesis's given is typed with Any
    validator = jsonschema.Draft202012Validator(
        TASK_SCHEMA, format_checker=jsonschema.FormatChecker()
    )
    assert (not task_problems(task)) == validator.is_valid(task), (task_problems(task), task)


@given(mutated(CONFIG, CONFIG_KEYS))
def test_configs(config: dict[str, object]) -> None:  # type: ignore[misc]  # hypothesis's given is typed with Any
    validator = jsonschema.Draft202012Validator(
        CONFIG_SCHEMA, format_checker=jsonschema.FormatChecker()
    )
    assert (not todo_config_problems(config)) == validator.is_valid(config), config


def test_the_real_files_are_valid_by_both() -> None:
    task_validator = jsonschema.Draft202012Validator(
        TASK_SCHEMA, format_checker=jsonschema.FormatChecker()
    )
    assert all(task_validator.is_valid(t) and not task_problems(t) for t in TASKS)
    assert jsonschema.Draft202012Validator(CONFIG_SCHEMA).is_valid(CONFIG)
    assert not todo_config_problems(CONFIG)
