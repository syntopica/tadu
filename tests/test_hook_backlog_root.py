from pathlib import Path

from tadu.hook_backlog_root import hook_backlog_root


def repo(tmp_path: Path) -> Path:
    tmp_path.mkdir(exist_ok=True)
    (tmp_path / "TODO.md").write_text("# TODO\n")
    return tmp_path


def test_edit_of_a_backlog_file(tmp_path: Path) -> None:
    root = repo(tmp_path)
    for tool in ("Edit", "Write", "MultiEdit"):
        payload = {"tool_name": tool, "tool_input": {"file_path": str(root / "TODO_LOG.md")}}
        assert hook_backlog_root(payload) == root


def test_edit_of_another_file_or_another_tool(tmp_path: Path) -> None:
    root = repo(tmp_path)
    assert (
        hook_backlog_root({"tool_name": "Edit", "tool_input": {"file_path": str(root / "a.py")}})
        is None
    )
    assert (
        hook_backlog_root({"tool_name": "Read", "tool_input": {"file_path": str(root / "TODO.md")}})
        is None
    )


def test_shell_writes_and_closes(tmp_path: Path) -> None:
    root = repo(tmp_path)
    (root / "sub").mkdir()

    def bash(command: str, cwd: Path = root) -> dict[str, object]:
        return {"tool_name": "Bash", "tool_input": {"command": command}, "cwd": str(cwd)}

    assert hook_backlog_root(bash("python3 -c \"open('TODO.md','w')\"")) == root
    assert (
        hook_backlog_root(bash("tadu close --match a --evidence e --write", root / "sub")) == root
    )
    assert hook_backlog_root(bash(f"cd {root} && sed -i '' s/a/b/ TODO.md", "/")) == root
    assert hook_backlog_root(bash("cd sub && tadu close --match a --evidence e --write")) == root


def test_shell_reads_and_dry_runs_are_ignored(tmp_path: Path) -> None:
    root = repo(tmp_path)
    for command in (
        "grep -n fix TODO.md",
        "cat TODO.md > /dev/null",
        "grep x TODO.md 2>&1",
        "tadu close --match a --evidence e",
        "git status",
    ):
        payload = {"tool_name": "Bash", "tool_input": {"command": command}, "cwd": str(root)}
        assert hook_backlog_root(payload) is None


def test_writes_into_another_repository(tmp_path: Path) -> None:
    here, there = repo(tmp_path / "a"), repo(tmp_path / "b")
    for command in (f"printf x > {there}/TODO.md", f"tadu close {there} --match a --write"):
        payload = {"tool_name": "Bash", "tool_input": {"command": command}, "cwd": str(here)}
        assert hook_backlog_root(payload) == there
    copy = {"tool_name": "Bash", "tool_input": {"command": f"cp {there}/TODO.md TODO.md"}}
    assert hook_backlog_root({**copy, "cwd": str(here)}) == here


def test_quoted_redirect_with_spaces(tmp_path: Path) -> None:
    there = repo(tmp_path / "r s")
    command = f'printf x > "{there}/TODO.md"'
    payload = {"tool_name": "Bash", "tool_input": {"command": command}, "cwd": "/"}
    assert hook_backlog_root(payload) == there
