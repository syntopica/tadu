import threading
from pathlib import Path

import pytest
from fake_github import fake_github
from team_workspace import team_workspace

from tadu.board_session import BoardSession
from tadu.github_sign_in import GithubSignIn
from tadu.load_workspace import load_workspace
from tadu.readable_repositories import readable_repositories
from tadu.repository_entry import RepositoryEntry
from tadu.sign_in_settings import ACCESS_SECONDS, DENIED_SECONDS, RETRY_SECONDS
from tadu.signed_out_error import SignedOutError
from tadu.workspace import Workspace

LIST = "GET /api/user/repos?per_page=100&page=1"
ANA = BoardSession("s-tok-ana", "ana", 10**12, "tok-ana")


def seen(
    sign_in: GithubSignIn, session: BoardSession, workspace: Workspace, now: float
) -> tuple[frozenset[str], int | None]:
    access = readable_repositories(sign_in, session, workspace, now)
    assert access.unconfirmed is False
    return access.readable, access.failed


@pytest.fixture
def workspace(tmp_path: Path) -> Workspace:
    return load_workspace(team_workspace(tmp_path))


def with_repositories(workspace: Workspace, *remotes: str) -> Workspace:
    extra = tuple(RepositoryEntry(r.rpartition("/")[2], f"https://github.com/{r}") for r in remotes)
    return Workspace(workspace.root, (*workspace.repositories, *extra), (), (), ())


def test_the_list_answers_and_the_rest_is_asked_once(workspace: Workspace) -> None:
    with fake_github({"ana": {"acme/shop", "acme/other"}}) as github:
        sign_in = github.sign_in()
        assert seen(sign_in, ANA, workspace, 0.0) == (frozenset({"shop"}), None)
        assert github.requests == [LIST, "GET /api/repos/acme/vault"]
        other_tab = BoardSession("s-tok-ana", "ana", 10**12, "tok-ana")
        assert seen(sign_in, other_tab, workspace, 1.0)[0] == {"shop"}
        assert len(github.requests) == 2


def test_the_list_is_asked_again_with_its_etag(workspace: Workspace) -> None:
    with fake_github({"ana": {"acme/shop"}}) as github:
        sign_in = github.sign_in()
        seen(sign_in, ANA, workspace, 0.0)
        seen(sign_in, ANA, workspace, ACCESS_SECONDS)
        assert github.requests[2:] == [LIST]
        assert github.not_modified == 1
        seen(sign_in, ANA, workspace, DENIED_SECONDS)
        assert github.requests[3:] == [LIST, "GET /api/repos/acme/vault"]
        assert github.not_modified == 2


def test_access_given_shows_at_the_next_list(workspace: Workspace) -> None:
    with fake_github({"ana": {"acme/shop"}}) as github:
        sign_in = github.sign_in()
        seen(sign_in, ANA, workspace, 0.0)
        github.readable["ana"].add("acme/vault")
        assert seen(sign_in, ANA, workspace, 1.0)[0] == {"shop"}
        later = seen(sign_in, ANA, workspace, ACCESS_SECONDS)
        assert later == (frozenset({"shop", "vault"}), None)


def test_access_taken_away_hides_within_the_list_time(workspace: Workspace) -> None:
    with fake_github({"ana": {"acme/shop"}}) as github:
        sign_in = github.sign_in()
        seen(sign_in, ANA, workspace, 0.0)
        github.readable["ana"].clear()
        assert seen(sign_in, ANA, workspace, ACCESS_SECONDS - 1)[0] == {"shop"}
        assert seen(sign_in, ANA, workspace, ACCESS_SECONDS)[0] == set()
        assert github.requests[-2:] == [LIST, "GET /api/repos/acme/shop"]


def test_a_public_repository_in_no_list_is_asked_about(workspace: Workspace) -> None:
    with fake_github({}, public=frozenset({"acme/vault"})) as github:
        sign_in = github.sign_in()
        assert seen(sign_in, ANA, workspace, 0.0)[0] == {"vault"}
        seen(sign_in, ANA, workspace, ACCESS_SECONDS)
        assert github.repository_requests() == ["acme/shop", "acme/vault", "acme/vault"]
        assert github.not_modified == 2


def test_pages_are_all_read(workspace: Workspace, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("tadu.listed_repositories.LIST_PAGE_SIZE", 1)
    with fake_github({"ana": {"acme/shop", "acme/vault", "acme/zoo"}}) as github:
        found = seen(github.sign_in(), ANA, workspace, 0.0)
        assert found == (frozenset({"shop", "vault"}), None)
        assert sorted(github.requests) == [
            f"GET /api/user/repos?per_page=1&page={page}" for page in (1, 2, 3)
        ]


def test_a_list_too_long_gives_way_to_single_checks(
    workspace: Workspace, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("tadu.listed_repositories.LIST_PAGE_SIZE", 1)
    monkeypatch.setattr("tadu.listed_repositories.LIST_PAGE_LIMIT", 2)
    with fake_github({"ana": {"acme/shop", "acme/vault", "acme/zoo"}}) as github:
        found = seen(github.sign_in(), ANA, workspace, 0.0)
        assert found == (frozenset({"shop", "vault"}), None)
        assert github.requests[0] == "GET /api/user/repos?per_page=1&page=1"
        assert github.repository_requests() == ["acme/shop", "acme/vault"]


def test_a_failed_list_hides_and_backs_off(workspace: Workspace) -> None:
    limited = BoardSession("s-tok-limited", "limited", 10**12, "tok-limited")
    with fake_github({"limited": {"acme/shop"}}) as github:
        sign_in = github.sign_in()
        assert seen(sign_in, limited, workspace, 0.0) == (frozenset(), 403)
        assert seen(sign_in, limited, workspace, RETRY_SECONDS - 1)[1] == 403
        assert github.requests == [LIST]
        assert seen(sign_in, limited, workspace, RETRY_SECONDS)[1] == 403
        assert github.requests == [LIST, LIST]


def test_a_check_that_cannot_tell_hides_backs_off_and_retries(workspace: Workspace) -> None:
    flaky = with_repositories(workspace, "acme/flaky")
    with fake_github({"ana": {"acme/shop"}}) as github:
        sign_in = github.sign_in()
        assert seen(sign_in, ANA, flaky, 0.0) == (frozenset({"shop"}), 502)
        seen(sign_in, ANA, flaky, RETRY_SECONDS - 1)
        assert github.repository_requests() == ["acme/flaky", "acme/vault"]
        assert seen(sign_in, ANA, workspace, RETRY_SECONDS) == (
            frozenset({"shop"}),
            None,
        )
        assert len(github.requests) == 3


def test_a_revoked_token_signs_out(workspace: Workspace) -> None:
    with fake_github({"ana": {"acme/shop"}}) as github:
        sign_in = github.sign_in()
        with pytest.raises(SignedOutError):
            seen(
                sign_in, BoardSession("s-tok-revoked", "ana", 10**12, "tok-revoked"), workspace, 0.0
            )
        shop_only = Workspace(workspace.root, workspace.repositories[:1], (), (), ())
        seen(sign_in, ANA, shop_only, 0.0)
        with pytest.raises(SignedOutError):
            seen(
                sign_in, BoardSession("s-tok-revoked", "ana", 10**12, "tok-revoked"), workspace, 1.0
            )


def test_loads_at_once_share_one_refresh(workspace: Workspace) -> None:
    with fake_github({"ana": {"acme/shop"}}) as github:
        sign_in = github.sign_in()
        start = threading.Barrier(4)
        found: list[frozenset[str]] = []

        def load() -> None:
            start.wait()
            found.append(seen(sign_in, ANA, workspace, 0.0)[0])

        threads = [threading.Thread(target=load) for _ in range(4)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        assert found == [frozenset({"shop"})] * 4
        assert github.requests == [LIST, "GET /api/repos/acme/vault"]


def test_without_github_remotes_nothing_is_asked(workspace: Workspace) -> None:
    only_local = Workspace(workspace.root, (RepositoryEntry("notes", None),), (), (), ())
    with fake_github({}) as github:
        assert seen(github.sign_in(), ANA, only_local, 0.0) == (frozenset(), None)
        assert github.requests == []


def test_people_do_not_share_answers(workspace: Workspace) -> None:
    with fake_github({"ana": {"acme/shop"}, "bo": {"acme/vault"}}) as github:
        sign_in = github.sign_in()
        assert seen(sign_in, ANA, workspace, 0.0)[0] == {"shop"}
        bo = BoardSession("s-tok-bo", "bo", 10**12, "tok-bo")
        assert seen(sign_in, bo, workspace, 1.0)[0] == {"vault"}
        assert github.requests.count(LIST) == 2


def test_a_token_revoked_between_the_list_and_a_check_signs_out(
    workspace: Workspace, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("tadu.ask_repositories.repository_status", lambda *_args: (401, None, None))
    with fake_github({"ana": {"acme/shop"}}) as github:
        with pytest.raises(SignedOutError):
            readable_repositories(github.sign_in(), ANA, workspace, 0.0)
        assert github.requests == [LIST]
