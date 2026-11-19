from tadu.history_line import HistoryLine
from tadu.line_facts import line_facts


def line(op: str, field: str) -> HistoryLine:
    return {"op": op, "field": field, "text": "x"}


def test_counts_lines_added_and_removed_per_field_in_order() -> None:
    lines = [line("-", "notes"), line("+", "done_when"), line("+", "notes"), line("+", "done_when")]
    assert line_facts(lines) == ["notes: 1 added, 1 removed", "done_when: 2 added"]
    assert line_facts([line("-", "text")]) == ["text: 1 removed"]
    assert line_facts([]) == []
