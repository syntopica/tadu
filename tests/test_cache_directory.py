import sys
from pathlib import Path

import pytest

from tadu.cache_directory import cache_directory
from tadu.scan_task_folder import scan_task_folder


def test_explicit_directory_wins(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TADU_CACHE_DIR", "/somewhere")
    assert cache_directory() == Path("/somewhere")


@pytest.mark.skipif(sys.platform != "linux", reason="macOS and Windows keep the cache elsewhere")
def test_xdg_then_home(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("TADU_CACHE_DIR")
    monkeypatch.setenv("XDG_CACHE_HOME", "/xdg")
    assert cache_directory() == Path("/xdg/tadu")
    monkeypatch.delenv("XDG_CACHE_HOME")
    monkeypatch.setenv("HOME", str(tmp_path))
    assert cache_directory() == tmp_path / ".cache" / "tadu"


def test_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TADU_NO_CACHE", "1")
    assert cache_directory() is None


def test_scan_of_a_missing_folder_is_empty(tmp_path: Path) -> None:
    assert scan_task_folder(tmp_path / "missing") == {}


def test_scan_goes_into_subfolders(tmp_path: Path) -> None:
    (tmp_path / "2026" / "01").mkdir(parents=True)
    (tmp_path / "2026" / "01" / "t-1.json").write_text("{}")
    (tmp_path / "t-2.json").write_text("{}")
    assert sorted(scan_task_folder(tmp_path)) == ["2026/01/t-1.json", "t-2.json"]
