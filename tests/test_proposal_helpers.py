from http import HTTPStatus
from pathlib import Path
from types import SimpleNamespace

import pytest

from tadu.backlog_candidates import backlog_candidates
from tadu.default_head import default_head
from tadu.file_change import FileChange
from tadu.github_reply import GithubReply
from tadu.proposal_error import ProposalError
from tadu.proposal_field import proposal_field
from tadu.proposal_reply import proposal_reply
from tadu.remote_blobs import remote_blobs
from tadu.signed_out_error import SignedOutError
from tadu.stray_files import stray_files
from tadu.tree_entries import tree_entries


class Api(SimpleNamespace):
    """A RepositoryApi that answers from a table of path to answer."""

    def get(self, path: str) -> dict[str, object]:
        return self.answers[path]  # type: ignore[no-any-return]


def test_the_archived_years_of_the_log_are_candidates(tmp_path: Path) -> None:
    (tmp_path / "docs" / "todo-log").mkdir(parents=True)
    (tmp_path / "docs" / "todo-log" / "2025.md").write_text("")
    (tmp_path / "docs" / "todo-log" / "notes.md").write_text("")
    names = {p.name for p in backlog_candidates(tmp_path)}
    assert "2025.md" in names
    assert "notes.md" not in names


def test_default_head_names_the_commit_and_its_tree() -> None:
    api = Api(
        answers={
            "/git/ref/heads/main": {"object": {"sha": "c1"}},
            "/git/commits/c1": {"tree": {"sha": "t1"}},
        }
    )
    assert default_head(api, "main") == ("c1", "t1")  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "answers",
    [
        {"/git/ref/heads/main": {"object": "x"}},
        {"/git/ref/heads/main": {"object": {"sha": "c1"}}, "/git/commits/c1": {"tree": 3}},
    ],
)
def test_default_head_refuses_answers_that_do_not_name_it(answers: dict[str, object]) -> None:
    with pytest.raises(ProposalError):
        default_head(Api(answers=answers), "main")  # type: ignore[arg-type]


def test_a_missing_field_is_a_proposal_error() -> None:
    assert proposal_field({"a": "b"}, "a") == "b"
    with pytest.raises(ProposalError, match="a expected"):
        proposal_field({"a": 1}, "a")


def test_proposal_reply_tells_each_kind_of_answer() -> None:
    assert proposal_reply(GithubReply(201, {"x": 1})) == {"x": 1}
    with pytest.raises(SignedOutError):
        proposal_reply(GithubReply(HTTPStatus.UNAUTHORIZED))
    with pytest.raises(ProposalError, match="could not be reached"):
        proposal_reply(GithubReply(0))
    for reply in (GithubReply(403, {"message": "secret"}), GithubReply(200, [1])):
        with pytest.raises(ProposalError, match="refused the step") as refused:
            proposal_reply(reply)
        assert "secret" not in str(refused.value)


def test_a_truncated_tree_cannot_be_compared() -> None:
    whole = {
        "/git/trees/t?recursive=1": {
            "truncated": False,
            "tree": [
                {"path": "a", "type": "blob", "sha": "s"},
                {"path": "d", "type": "tree", "sha": "x"},
            ],
        }
    }
    assert remote_blobs(Api(answers=whole), "t") == {"a": "s"}  # type: ignore[arg-type]
    cut = {"/git/trees/t?recursive=1": {"truncated": True, "tree": []}}
    with pytest.raises(ProposalError, match="too large"):
        remote_blobs(Api(answers=cut), "t")  # type: ignore[arg-type]


def test_tree_entries_hold_text_or_delete_and_refuse_binary() -> None:
    entries = tree_entries([FileChange("a", None, b"x"), FileChange("b", b"y", None)])
    assert entries[0]["content"] == "x"
    assert entries[1]["sha"] is None
    with pytest.raises(ProposalError, match="UTF-8"):
        tree_entries([FileChange("c", None, b"\xff")])


def test_stray_files_lists_what_is_not_known(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("")
    (tmp_path / ".x.tmp").write_text("")
    assert stray_files(tmp_path, {"TODO.md": b""}) == [".x.tmp"]
