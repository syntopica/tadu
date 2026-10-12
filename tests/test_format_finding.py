import json

from tadu.finding import Finding
from tadu.format_finding import format_finding

FINDING = Finding("T001", "error", "a/TODO.md", 3, "boom")


def test_text_form() -> None:
    assert format_finding(FINDING, as_json=False) == "a/TODO.md:3: error T001 boom"


def test_json_form() -> None:
    assert json.loads(format_finding(FINDING, as_json=True)) == {
        "code": "T001",
        "severity": "error",
        "path": "a/TODO.md",
        "line": 3,
        "message": "boom",
    }
