import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CODE = re.compile(r'"([A-Z]\d{3})"')


def emitted_codes() -> set[str]:
    sources = (REPO_ROOT / "tadu").glob("*.py")
    return {code for path in sources for code in CODE.findall(path.read_text(encoding="utf-8"))}


def test_doctor_docs_list_every_code_the_cli_can_emit() -> None:
    docs = (REPO_ROOT / "docs" / "doctor.md").read_text(encoding="utf-8")
    documented = set(re.findall(r"^\| ([A-Z]\d{3}) \|", docs, re.MULTILINE))
    assert emitted_codes() == documented
    assert len(documented) == 55
