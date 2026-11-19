import argparse
from datetime import date
from pathlib import Path

import pytest

from tadu.item_match import item_match

ID = "t-3f2a1b4c-5d6e-4f70-8a91-b2c3d4e5f607"


def args(root: Path, **given: object) -> argparse.Namespace:
    return argparse.Namespace(paths=[str(root)], workspace=None, repository=None, **given)


def test_text_or_the_line_a_key_names(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "TODO.md").write_text(f"# TODO\n\n- [ ] Ship it.\n\n  ID: {ID}\n")
    today = date(2026, 11, 4)
    assert item_match("mark", args(tmp_path, id=None, match="Ship"), today) == "Ship"
    assert item_match("mark", args(tmp_path, id=ID[:12], match=None), today) == 2
    assert item_match("close", args(tmp_path, id="t-0000dead", match=None), today) is None
    assert capsys.readouterr().err == "tadu close: 0 open items have key t-0000dead\n"
