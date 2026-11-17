from pathlib import Path

import pytest
from python_rules import rule_findings

SOURCES = sorted((Path(__file__).parent.parent / "tadu").glob("*.py"))


def codes(source: str, module: str = "x.py") -> list[tuple[str, int]]:
    return [(code, line) for code, line, _ in rule_findings(source, module)]


def test_every_tadu_module_follows_the_rules() -> None:
    found = [
        f"tadu/{path.name}:{line}: {code} {text}"
        for path in SOURCES
        for code, line, text in rule_findings(path.read_text(encoding="utf-8"), path.name)
    ]
    assert len(SOURCES) > 250
    assert found == [], (
        "P001 a path's name used as if it identified the path; P002 keys that may collide "
        "and silently replace an entry; P003 a filesystem write outside write_file_atomically "
        "and create_file_exclusively; P004 a replace without backlog_unchanged first. Fix the "
        "shape, or when it is safe say why with `# path-name: ...`, `# keys: ...` or "
        "`# writes: ...` on the line or in the comments right above it (tests/python_rules.py)."
    )


def test_the_folder_name_bug_is_caught() -> None:
    old_mcp_root = (
        "def root(scope, repository):\n"
        "    roots = {}\n"
        "    for text in scope.paths:\n"
        "        roots[Path(text).resolve().name] = Path(text)\n"
    )
    assert codes(old_mcp_root) == [("P001", 4), ("P002", 4)]
    old_path_cards = (
        "def cards(roots):\n"
        "    for text in roots:\n"
        "        root = Path(text).resolve()\n"
        "        read(root, root.name)\n"
    )
    assert codes(old_path_cards) == [("P001", 4)]


@pytest.mark.parametrize(
    "source",
    [
        "def f(root: Path) -> str:\n    return root.name\n",
        "def f(root: Path | None):\n    return root.stem\n",
        "def f(path):\n    return (path / 'x').parent.name\n",
        "def f(texts):\n    roots = [Path(t) for t in texts]\n    return [r.name for r in roots]\n",
    ],
)
def test_a_path_name_is_found(source: str) -> None:
    assert [code for code, _ in codes(source)] == ["P001"]


@pytest.mark.parametrize(
    "source",
    [
        "def f(view):\n    return view.name\n",
        "def f(root: Path):\n    # path-name: only a label for the message.\n    return root.name\n",
        "def f(d):\n    return {k: v for k, v in d.items() if v}\n",
        "def f(rows):\n    for row in rows:\n        row[0] = 1\n",
        "def f(text):\n    return text.replace('a', 'b')\n",
        "def f(path: Path):\n    return path.open('rb')\n",
        "def f():\n    return os.open('x', os.O_RDONLY)\n",
    ],
)
def test_safe_shapes_pass(source: str) -> None:
    assert codes(source) == []


@pytest.mark.parametrize(
    "source",
    [
        "def f(rows):\n    return {row.name: row for row in rows}\n",
        "def f(rows):\n    return dict.fromkeys(rows)\n",
        "def f(rows):\n    seen = {}\n    for row in rows:\n        seen[row.key] = row\n",
        "def f(rows):\n    # keys:\n    return {row.name: row for row in rows}\n",
    ],
)
def test_keys_that_may_collide_need_a_reason(source: str) -> None:
    assert [code for code, _ in codes(source)] == ["P002"]


@pytest.mark.parametrize(
    "source",
    [
        "def f(path: Path):\n    path.write_text('x')\n",
        "def f(path: Path, target):\n    path.replace(target)\n",
        "def f(name):\n    open(name, 'a')\n",
        "def f(path: Path):\n    path.open(mode='w')\n",
        "def f(name):\n    os.remove(name)\n",
        "def f(name):\n    os.open(name, os.O_WRONLY | os.O_CREAT)\n",
        "def f(name):\n    shutil.rmtree(name)\n",
        "def f():\n    tempfile.mkstemp()\n",
    ],
)
def test_writes_outside_the_writers_need_a_reason(source: str) -> None:
    assert [code for code, _ in codes(source)] == ["P003"]
    assert codes(source, "write_file_atomically.py") == []


def test_a_replace_needs_a_check_that_the_file_is_unchanged() -> None:
    unchecked = "def f(path, text):\n    write_file_atomically(path, text)\n"
    assert codes(unchecked) == [("P004", 1)]
    checked = (
        "def f(path, before, text):\n"
        "    if backlog_unchanged((path, before)):\n"
        "        write_file_atomically(path, text)\n"
    )
    assert codes(checked) == []
