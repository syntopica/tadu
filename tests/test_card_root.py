from pathlib import Path

import pytest

from tadu.card_root import card_root
from tadu.local_config import LocalConfig


def test_roots_given_as_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "shop").mkdir()
    assert card_root((str(tmp_path / "shop"),), None, "shop") == (tmp_path / "shop").resolve()
    monkeypatch.chdir(tmp_path / "shop")
    assert card_root((), None, "shop") == (tmp_path / "shop").resolve()


def test_workspace_paths(tmp_path: Path) -> None:
    local = LocalConfig({"shop": tmp_path / "checkout"}, None, None)
    assert card_root((), local, "shop") == tmp_path / "checkout"
