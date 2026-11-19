import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CODE = re.compile(r'"([A-Z]\d{3})"')
# Quoted strings shaped like a code that are something else.
NOT_CODES = {"S256"}  # the PKCE challenge method of signing in with GitHub


def emitted_codes() -> set[str]:
    sources = (REPO_ROOT / "tadu").glob("*.py")
    found = {code for path in sources for code in CODE.findall(path.read_text(encoding="utf-8"))}
    return found - NOT_CODES


def test_readme_table_lists_every_code_the_cli_can_emit() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    documented = set(re.findall(r"^\| ([A-Z]\d{3}) \|", readme, re.MULTILINE))
    assert emitted_codes() == documented
    assert len(documented) == 62
