from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_DIRS = sorted(path.parent for path in REPO_ROOT.glob("skills/*/SKILL.md"))


def front_matter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    assert lines[0] == "---"
    end = lines.index("---", 1)
    fields: dict[str, str] = {}
    key = ""
    for line in lines[1:end]:
        if line.startswith((" ", "\t")):
            fields[key] = f"{fields[key]} {line.strip()}".strip()
            continue
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return fields


def test_both_skills_are_present() -> None:
    assert [path.name for path in SKILL_DIRS] == ["tadu-create", "tadu-work"]


@pytest.mark.parametrize("skill_dir", SKILL_DIRS, ids=lambda path: path.name)
def test_front_matter_names_the_directory(skill_dir: Path) -> None:
    fields = front_matter((skill_dir / "SKILL.md").read_text(encoding="utf-8"))
    assert fields["name"] == skill_dir.name
    assert fields["description"]


@pytest.mark.parametrize("skill_dir", SKILL_DIRS, ids=lambda path: path.name)
def test_format_reference_matches_the_spec(skill_dir: Path) -> None:
    copy = (skill_dir / "references" / "format.md").read_text(encoding="utf-8")
    spec = (REPO_ROOT / "spec" / "todo-format-v1.md").read_text(encoding="utf-8")
    first_line, _, rest = copy.partition("\n")
    assert first_line == "Copied from spec/todo-format-v1.md; the spec is authoritative."
    assert rest == spec


def test_rule_block_reference_matches_the_package_copy() -> None:
    copy = REPO_ROOT / "skills" / "tadu-create" / "references" / "rule-block.md"
    package = REPO_ROOT / "tadu" / "rule_block_v2.md"
    assert copy.read_bytes() == package.read_bytes()
