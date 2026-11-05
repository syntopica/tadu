from dataclasses import fields
from datetime import date

import pytest
from pydantic import TypeAdapter, ValidationError

from tadu.card_filter import CardFilter
from tadu.mcp_where import McpWhere

ADAPTER = TypeAdapter(McpWhere)


def test_has_the_card_filter_fields() -> None:
    assert [field.name for field in fields(McpWhere)] == [
        field.name for field in fields(CardFilter)
    ]


def test_parses_valid_criteria() -> None:
    where = ADAPTER.validate_python({"column": "blocked", "due_before": "2026-11-05"})
    assert where.column == "blocked"
    assert where.due_before == date(2026, 11, 5)


@pytest.mark.parametrize(
    "criteria",
    [{"colum": "blocked"}, {"column": "doing"}, {"priority": "critical"}, {"due_before": "soon"}],
)
def test_rejects_malformed_criteria(criteria: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        ADAPTER.validate_python(criteria)
