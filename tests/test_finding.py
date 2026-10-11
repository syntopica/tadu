import dataclasses

import pytest

from tadu.finding import Finding


def test_finding_is_frozen() -> None:
    finding = Finding("T001", "error", "TODO.md", 0, "no TODO.md")
    with pytest.raises(dataclasses.FrozenInstanceError):
        finding.code = "T002"  # type: ignore[misc]


def test_equal_fields_compare_equal() -> None:
    assert Finding("T001", "error", "TODO.md", 0, "no TODO.md") == Finding(
        "T001", "error", "TODO.md", 0, "no TODO.md"
    )
