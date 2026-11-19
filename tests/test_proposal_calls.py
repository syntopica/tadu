from pathlib import Path

import pytest
from team_workspace import team_workspace

from tadu.github_send import github_send
from tadu.proposal_error import ProposalError
from tadu.proposal_request import ProposalRequest
from tadu.propose_changes import propose_changes
from tadu.redirected_checkouts import REDIRECTED_CHECKOUTS
from tadu.resolve_proposal_target import resolve_proposal_target
from tadu.run_on_copy import run_on_copy
from tadu.write_call import write_call


def test_a_repository_without_a_github_remote_cannot_be_proposed_to(tmp_path: Path) -> None:
    workspace = team_workspace(tmp_path)
    with pytest.raises(ProposalError, match="no GitHub remote"):
        resolve_proposal_target(workspace, "notes")
    assert resolve_proposal_target(workspace, "shop").name == "acme/shop"


def test_an_unreachable_github_answers_status_zero() -> None:
    assert github_send("http://127.0.0.1:9/x", "t", {}).status == 0


def test_a_missing_token_sends_nothing() -> None:
    with pytest.raises(ProposalError, match="could not be reached"):
        propose_changes(None, None, "a/b", ProposalRequest("x", "add", {}, []))  # type: ignore[arg-type]


def test_a_change_that_writes_outside_the_backlog_is_not_proposed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace = team_workspace(tmp_path)

    def stray(*_: object) -> tuple[int, str, str]:
        (REDIRECTED_CHECKOUTS.get() or {})["shop"].joinpath("junk.bin").write_text("x")
        return 0, "", ""

    monkeypatch.setattr("tadu.run_on_copy.run_operation", stray)
    target = resolve_proposal_target(workspace, "shop")
    state = type("S", (), {"workspace": workspace, "allow": "write", "main": None})()
    with pytest.raises(ProposalError, match="more than the backlog"):
        run_on_copy(state, "add", {}, target)


def test_write_call_ignores_what_is_not_a_write() -> None:
    state = type("S", (), {"allow": "write"})()
    assert write_call("/api/op/add", b"\xff", state) is None
    assert write_call("/api/op/add", b"[]", state) is None
    assert write_call("/api/other", b"{}", state) is None
    assert write_call("/api/op/add", b'{"title": "t"}', state) == ("add", {"title": "t"})
