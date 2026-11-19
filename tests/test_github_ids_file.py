from pathlib import Path

import pytest

from tadu.confirmed_repository import confirmed_repository
from tadu.github_sign_in import GithubSignIn
from tadu.parse_github_ids import parse_github_ids
from tadu.read_github_ids import read_github_ids
from tadu.record_github_id import record_github_id
from tadu.render_github_ids import render_github_ids
from tadu.repository_entry import RepositoryEntry
from tadu.repository_pins import RepositoryPins


def test_render_and_parse_round_trip_sorted() -> None:
    text = render_github_ids({"vault": 2, "shop": 1})
    assert text == '{\n  "version": 1,\n  "github_ids": {\n    "shop": 1,\n    "vault": 2\n  }\n}\n'
    assert parse_github_ids(text) == {"shop": 1, "vault": 2}


@pytest.mark.parametrize(
    "text",
    [
        "",
        "[]",
        '{"version": 2, "github_ids": {}}',
        '{"version": 1}',
        '{"version": 1, "github_ids": []}',
        '{"version": 1, "github_ids": {"shop": "1"}}',
        '{"version": 1, "github_ids": {"shop": 0}}',
        '{"version": 1, "github_ids": {"shop": true}}',
        '{"version": 1, "github_ids": {"shop": 1.5}}',
    ],
)
def test_anything_else_is_an_error(tmp_path: Path, text: str) -> None:
    with pytest.raises(ValueError):  # noqa: PT011 - json's and tadu's messages differ
        parse_github_ids(text)
    path = tmp_path / "ids.json"
    path.write_text(text)
    with pytest.raises(ValueError, match=r"ids\.json: "):
        read_github_ids(path)


def test_read_a_missing_or_unreadable_file(tmp_path: Path) -> None:
    assert read_github_ids(tmp_path / "none.json") == ({}, None)
    (tmp_path / "dir.json").mkdir()
    with pytest.raises(ValueError, match=r"dir\.json: .*could not be read"):
        read_github_ids(tmp_path / "dir.json")
    (tmp_path / "latin.json").write_bytes(b"\xff")
    with pytest.raises(ValueError, match="not valid UTF-8"):
        read_github_ids(tmp_path / "latin.json")


def test_record_creates_adds_and_keeps_what_another_board_wrote(tmp_path: Path) -> None:
    path = tmp_path / "ids.json"
    assert record_github_id(path, "shop", 1) == {"shop": 1}
    assert record_github_id(path, "vault", 2) == {"shop": 1, "vault": 2}
    assert record_github_id(path, "shop", 9) == {"shop": 1, "vault": 2}
    assert parse_github_ids(path.read_text()) == {"shop": 1, "vault": 2}


def test_record_never_overwrites_a_file_changed_meanwhile(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "ids.json"
    record_github_id(path, "shop", 1)
    stale = render_github_ids({})
    monkeypatch.setattr("tadu.record_github_id.read_github_ids", lambda _path: ({}, stale))
    with pytest.raises(OSError, match="changed while the board wrote to it"):
        record_github_id(path, "vault", 2)
    assert parse_github_ids(path.read_text()) == {"shop": 1}


def test_two_boards_agree_on_the_first_id(tmp_path: Path) -> None:
    path = tmp_path / "ids.json"
    first, second = RepositoryPins(path), RepositoryPins(path)
    assert first.admit("shop", 1, None) is None
    assert second.admit("shop", 2, None) == 1
    assert second.admit("shop", 1, None) is None


def test_pins_in_memory_and_given_ids() -> None:
    pins = RepositoryPins()
    assert pins.admit("shop", 1, None) is None
    assert pins.admit("shop", 2, None) == 1
    assert pins.admit("vault", 5, 5) is None
    assert pins.admit("vault", 6, 5) == 5
    # A given id is not learned: without it, the first id seen is.
    assert pins.admit("vault", 6, None) is None
    assert pins.admit("vault", 5, None) == 6


def test_an_answer_without_an_id_confirms_nothing() -> None:
    sign_in = GithubSignIn("id", "secret", "http://h:1")
    entry = RepositoryEntry("shop", "https://github.com/acme/shop")
    assert confirmed_repository(sign_in, entry, "acme/shop", None) is False
    assert confirmed_repository(sign_in, entry, "acme/shop", 1) is True
