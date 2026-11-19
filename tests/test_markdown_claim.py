from pathlib import Path

import pytest

from tadu.cli import main

ID = "t-3f2a1b4c-5d6e-4f70-8a91-b2c3d4e5f607"


def todo(root: Path, state: str = " ", fields: str = "") -> Path:
    (root / "TODO.md").write_text(f"- [{state}] Ship it.\n\n  ID: {ID}\n{fields}")
    (root / "TODO_LOG.md").write_text("# Log\n")
    return root


def claim(root: Path, who: str, *extra: str) -> int:
    return main(["claim", ID[:12], "--as", who, "--root", str(root), *extra])


def test_claims_an_item_in_progress(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = todo(tmp_path, fields="\n  Assignees: bo\n")
    assert claim(root, "ana") == 0
    assert "would claim for ana" in capsys.readouterr().out
    assert claim(root, "ana", "--write") == 0
    text = (root / "TODO.md").read_text()
    assert text.startswith("- [~] Ship it.")
    assert "Assignees: bo, ana" in text
    capsys.readouterr()
    assert claim(root, "ana") == 2
    assert "in progress by bo" in capsys.readouterr().err


@pytest.mark.parametrize(
    ("item", "reason"),
    [
        (("!", ""), "it is blocked"),
        ((" ", "\n  Not before: 2999-01-01\n"), "it is deferred until 2999-01-01"),
        (("~", "\n  Assignees: bo\n"), "it is in progress by bo (use --force to take it over)"),
    ],
)
def test_refusals(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], item: tuple[str, str], reason: str
) -> None:
    assert claim(todo(tmp_path, *item), "ana") == 2
    assert capsys.readouterr().err == f"tadu claim: {ID}: {reason}\n"


def test_force_takes_it_over(tmp_path: Path) -> None:
    root = todo(tmp_path, "~", "\n  Assignees: bo\n")
    assert claim(root, "ana", "--force", "--write") == 0
    assert "Assignees: ana\n" in (root / "TODO.md").read_text()
    assert main(["claim", "t-00000000", "--as", "ana", "--root", str(root)]) == 2
