import json
import stat
import time
from pathlib import Path

import pytest

from tadu.session_store import SessionStore
from tadu.sign_in_settings import IDLE_TIMEOUT_SECONDS
from tadu.token_grant import TokenGrant

TOKEN = "ghu_tokenOfAna0123456789"  # noqa: S105
GRANT = TokenGrant(TOKEN, None, "ghr_refreshOfAna0123456789")
NOW = int(time.time())


def test_sessions_survive_a_new_store(tmp_path: Path) -> None:
    path = tmp_path / "sessions.json"
    cookie = SessionStore(path).create("Ana-Dev", GRANT, NOW)
    again = SessionStore(path)
    assert again.problem is None
    session = again.find(cookie, NOW + 1)
    assert session is not None
    assert (session.login, session.token, session.expires) == (
        "Ana-Dev",
        TOKEN,
        NOW + IDLE_TIMEOUT_SECONDS,
    )


def test_the_file_holds_no_token_no_cookie_and_only_its_owner_reads_it(tmp_path: Path) -> None:
    path = tmp_path / "sessions.json"
    cookie = SessionStore(path).create("Ana-Dev", GRANT, NOW)
    text = path.read_text()
    assert TOKEN not in text
    assert str(GRANT.refresh_token) not in text
    assert cookie not in text
    assert "Ana-Dev" in text
    assert stat.S_IMODE(path.stat().st_mode) == 0o600
    assert json.loads(text)["version"] == 2


def test_signing_out_removes_the_session_from_the_file(tmp_path: Path) -> None:
    path = tmp_path / "sessions.json"
    store = SessionStore(path)
    ana, bo = store.create("Ana-Dev", GRANT, NOW), store.create("bo", TokenGrant("t-bo"), NOW)
    store.drop(ana)
    store.drop("never-was")
    again = SessionStore(path)
    assert again.find(ana, NOW + 1) is None
    assert again.find(bo, NOW + 1) is not None
    assert len(json.loads(path.read_text())["sessions"]) == 1


def test_expired_sessions_are_not_loaded(tmp_path: Path) -> None:
    path = tmp_path / "sessions.json"
    cookie = SessionStore(path).create("Ana-Dev", GRANT, NOW - IDLE_TIMEOUT_SECONDS)
    assert json.loads(path.read_text())["sessions"]
    assert SessionStore(path).find(cookie, NOW - 1) is None


def test_a_record_edited_on_disk_opens_to_nothing(tmp_path: Path) -> None:
    path = tmp_path / "sessions.json"
    cookie = SessionStore(path).create("Ana-Dev", GRANT, 2_000_000_000.0)
    data = json.loads(path.read_text())
    (row,) = data["sessions"].values()
    row["expires"] += 10**6
    path.write_text(json.dumps(data))
    assert SessionStore(path).find(cookie, 2_000_000_001.0) is None


@pytest.mark.parametrize(
    "text",
    [
        "{",
        "[]",
        '{"version": 1, "sessions": {}}',
        '{"version": 2, "sessions": []}',
        '{"version": 2, "sessions": {"x": []}}',
        '{"version": 2, "sessions": {"x": {"login": "a", "expires": "1", "sealed": ""}}}',
        '{"version": 2, "sessions": {"x": {"login": "a", "expires": 1}}}',
    ],
)
def test_an_unreadable_file_signs_everyone_out_then_is_replaced(tmp_path: Path, text: str) -> None:
    path = tmp_path / "sessions.json"
    path.write_text(text)
    store = SessionStore(path)
    assert store.problem is not None
    assert store.problem.startswith(f"{path}: ")
    assert store.problem.endswith("; everyone signs in again")
    cookie = store.create("Ana-Dev", GRANT, NOW)
    assert SessionStore(path).find(cookie, NOW + 1) is not None


def test_a_file_that_cannot_be_written_keeps_sessions_in_memory(
    tmp_path: Path, capfd: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "sessions.json"
    path.mkdir()
    store = SessionStore(path)
    assert store.problem is not None
    assert "could not be read" in store.problem
    first = store.create("Ana-Dev", GRANT, NOW)
    store.create("bo", TokenGrant("t-bo"), NOW)
    assert store.find(first, NOW + 1) is not None
    assert capfd.readouterr().err.count("tadu board: warning: cannot save sessions") == 1
    path.rmdir()
    store.drop(first)
    assert path.is_file()
    path.unlink()
    path.mkdir()
    store.drop(store.create("cy", TokenGrant("t-cy"), NOW))
    assert capfd.readouterr().err.count("tadu board: warning: cannot save sessions") == 1


def test_a_file_another_process_changed_is_left_alone(
    tmp_path: Path, capfd: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "sessions.json"
    store = SessionStore(path)
    store.create("Ana-Dev", GRANT, NOW)
    path.write_text('{"version": 2, "sessions": {}}\n')
    cookie = store.create("bo", TokenGrant("t-bo"), NOW)
    assert store.find(cookie, NOW + 1) is not None
    assert path.read_text() == '{"version": 2, "sessions": {}}\n'
    assert "changed outside this board" in capfd.readouterr().err
