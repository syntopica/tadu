from tadu.canonical_arguments import canonical_arguments
from tadu.operations import OPERATIONS
from tadu.tool_params import tool_params

ADD = tool_params(OPERATIONS["add"])
CLAIM = tool_params(OPERATIONS["claim"])


def test_aliases_become_the_schema_names() -> None:
    given = {"title": "T", "notes": ["a"], "assignee": ["ana"], "label": "ux", "links": "https://x"}
    assert canonical_arguments(ADD, given) == {
        "title": "T",
        "note": ["a"],
        "assignees": ["ana"],
        "labels": ["ux"],
        "link": ["https://x"],
    }
    assert canonical_arguments(CLAIM, {"key": "t-1", "as": "ana"}) == {"id": "t-1", "who": "ana"}


def test_one_text_for_a_list_is_a_list_of_it() -> None:
    assert canonical_arguments(ADD, {"note": "Seen twice."}) == {"note": ["Seen twice."]}
    assert canonical_arguments(ADD, {"title": "T"}) == {"title": "T"}


def test_what_cannot_be_renamed_is_left_for_the_schema_check() -> None:
    assert canonical_arguments(ADD, ["x"]) == ["x"]
    assert canonical_arguments(ADD, {"note": ["a"], "notes": ["b"]}) == {
        "note": ["a"],
        "notes": ["b"],
    }
    assert canonical_arguments(ADD, {"labels": ["a"], "label": "b"}) == {
        "labels": ["a"],
        "label": "b",
    }
    assert canonical_arguments(CLAIM, {"as": "ana", "person": "bo"}) == {
        "who": "ana",
        "person": "bo",
    }
    assert canonical_arguments(ADD, {"colour": "red"}) == {"colour": "red"}
