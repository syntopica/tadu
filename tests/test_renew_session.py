import threading
from collections.abc import Iterator

import pytest
from board_clock import BoardClock
from fake_github import FakeGithub, fake_github

from tadu.board_session import BoardSession
from tadu.exchange_github_code import exchange_github_code
from tadu.github_sign_in import GithubSignIn
from tadu.renew_session import renew_session
from tadu.sign_in_settings import REFRESH_MARGIN_SECONDS
from tadu.signed_out_error import SignedOutError
from tadu.token_grant import TokenGrant


def signed_in(github: FakeGithub, code: str = "code-ana") -> tuple[GithubSignIn, str, BoardSession]:
    sign_in = github.sign_in()
    grant = exchange_github_code(sign_in, code, "verifier")
    assert grant is not None
    assert grant.expires is not None
    cookie = sign_in.sessions.create("ana", grant, grant.expires - github.token_seconds)
    session = sign_in.sessions.find(cookie, grant.expires - github.token_seconds)
    assert session is not None
    return sign_in, cookie, session


@pytest.fixture
def clock(monkeypatch: pytest.MonkeyPatch) -> BoardClock:
    """One clock for the board and the fake GitHub: a renewed token expires 8 hours after
    it is renewed, as GitHub's do, so it is not due again at once."""
    return BoardClock(monkeypatch)


@pytest.fixture
def github(clock: BoardClock) -> Iterator[FakeGithub]:
    assert clock.now
    with fake_github({}) as fake:
        yield fake


def test_a_token_not_due_is_used_as_it_is(github: FakeGithub) -> None:
    sign_in, cookie, session = signed_in(github)
    assert session.token_expires is not None
    due = session.token_expires - REFRESH_MARGIN_SECONDS
    assert renew_session(sign_in, cookie, due - 1) == session
    assert github.refreshes == 0


def test_a_token_due_is_renewed_and_kept(github: FakeGithub, clock: BoardClock) -> None:
    sign_in, cookie, session = signed_in(github)
    clock.advance(github.token_seconds - REFRESH_MARGIN_SECONDS)
    renewed = renew_session(sign_in, cookie, clock.now)
    assert renewed.token not in {None, session.token}
    assert renewed.refresh_token not in {None, session.refresh_token}
    assert sign_in.sessions.find(cookie, clock.now) == renewed
    assert renew_session(sign_in, cookie, clock.now) == renewed
    assert github.refreshes == 1


def test_requests_at_once_renew_once(github: FakeGithub, clock: BoardClock) -> None:
    sign_in, cookie, session = signed_in(github)
    clock.advance(github.token_seconds + 1)
    start = threading.Barrier(6)
    got: list[str | None] = []

    def load() -> None:
        start.wait()
        got.append(renew_session(sign_in, cookie, clock.now).token)

    threads = [threading.Thread(target=load) for _ in range(6)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert github.refreshes == 1
    assert len(set(got)) == 1
    assert got[0] not in {None, session.token}
    assert renew_session(sign_in, cookie, clock.now).token == got[0]
    assert github.refreshes == 1


def test_github_unreachable_goes_on_with_what_still_works(github: FakeGithub) -> None:
    sign_in, cookie, session = signed_in(github)
    assert session.token_expires is not None
    github.token_endpoint_down = True
    soon = session.token_expires - 1
    assert renew_session(sign_in, cookie, soon).token == session.token
    assert renew_session(sign_in, cookie, soon, force=True).token is None
    assert renew_session(sign_in, cookie, session.token_expires).token is None
    assert sign_in.sessions.find(cookie, soon) == session
    github.token_endpoint_down = False
    assert renew_session(sign_in, cookie, session.token_expires).token not in {None, session.token}


def test_github_refusing_to_renew_signs_out(github: FakeGithub) -> None:
    sign_in, cookie, session = signed_in(github)
    github.revoke_app("ana")
    with pytest.raises(SignedOutError):
        renew_session(sign_in, cookie, float(session.token_expires or 0))


def test_an_oauth_app_token_is_never_due_and_cannot_be_renewed(github: FakeGithub) -> None:
    sign_in = github.sign_in()
    cookie = sign_in.sessions.create("ana", TokenGrant("tok-ana"), 0.0)
    assert renew_session(sign_in, cookie, 10**6).token == "tok-ana"  # noqa: S105
    with pytest.raises(SignedOutError):
        renew_session(sign_in, cookie, 10**6, force=True)
    assert github.refreshes == 0


def test_no_session_signs_out(github: FakeGithub) -> None:
    with pytest.raises(SignedOutError):
        renew_session(github.sign_in(), "nobody", 0.0)


def test_a_session_that_ends_while_waiting_signs_out(
    github: FakeGithub, monkeypatch: pytest.MonkeyPatch
) -> None:
    sign_in, cookie, session = signed_in(github)
    store = sign_in.sessions
    lock = store.lock

    def lock_then_end(value: str) -> threading.Lock:
        store.drop(value)
        return lock(value)

    monkeypatch.setattr(store, "lock", lock_then_end)
    with pytest.raises(SignedOutError):
        renew_session(sign_in, cookie, float(session.token_expires or 0))
