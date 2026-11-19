import json
from dataclasses import replace

import pytest

from tadu.board_session import BoardSession
from tadu.open_session import open_session
from tadu.seal_session import seal_session
from tadu.session_id import session_id
from tadu.session_secret import session_secret

COOKIE = "Zm9vYmFyYmF6cXV4LWEtcmFuZG9tLWNvb2tpZS12YWx1ZQ"
TOKEN = "ghu_16C7e42F292c6912E7710c838347Ae178B4a"  # noqa: S105
REFRESH = "ghr_1B4a2e77838347a7E420ce178F2E7c6912E169246c34E1ccbF66C46812d16D5B1A9Dc86A1498"


def session(**changes: object) -> BoardSession:
    base = BoardSession(session_id(COOKIE), "Ana-Dev", 1_000, TOKEN, 900, REFRESH)
    return replace(base, **changes)  # type: ignore[arg-type]


def test_the_cookie_opens_what_it_sealed() -> None:
    assert open_session(COOKIE, seal_session(COOKIE, session())) == session()
    oauth_app = session(token_expires=None, refresh_token=None)
    assert open_session(COOKIE, seal_session(COOKIE, oauth_app)) == oauth_app


def test_nothing_stored_reveals_a_token_or_the_cookie() -> None:
    stored = seal_session(COOKIE, session())
    kept = json.dumps([session_id(COOKIE), stored.login, stored.expires, stored.sealed])
    for secret in (TOKEN, REFRESH, COOKIE, TOKEN[4:20], REFRESH[4:20], COOKIE[:16]):
        assert secret not in kept
    assert (stored.login, stored.expires) == ("Ana-Dev", 1_000)
    assert seal_session(COOKIE, session()).sealed != stored.sealed
    assert session_id(COOKIE + "x") != session_id(COOKIE)
    assert len(session_id(COOKIE)) == 64


def test_secrets_are_hkdf_per_purpose() -> None:
    assert session_secret(COOKIE, "id") != session_secret(COOKIE, "key")
    assert len(session_secret(COOKIE, "key")) == 32
    assert session_id(COOKIE) == session_secret(COOKIE, "id").hex()


@pytest.mark.parametrize(
    "change",
    [
        {"login": "Bo"},
        {"expires": 10**12},
        {"sealed": "gAAAAAB" + "A" * 90},
        {"sealed": "not a fernet token"},
    ],
)
def test_an_edited_record_does_not_open(change: dict[str, object]) -> None:
    stored = seal_session(COOKIE, session())
    assert open_session(COOKIE, replace(stored, **change)) is None  # type: ignore[arg-type]


def test_another_cookie_opens_nothing() -> None:
    stored = seal_session(COOKIE, session())
    assert open_session(COOKIE[:-1] + "A", stored) is None
    assert open_session("", stored) is None
