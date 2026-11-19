from tadu.git_commit import GitCommit
from tadu.history_event import HistoryEvent
from tadu.history_order import history_order
from tadu.markdown_items import markdown_items

(ITEM,) = markdown_items("- [ ] A.", "shop", "TODO.md")


def event(sha: str, day: int) -> tuple[GitCommit, HistoryEvent]:
    commit = GitCommit(sha, sha, (), f"2026-11-{day:02d}T09:00:00+00:00", "Ana", sha, ())
    return commit, HistoryEvent(commit, None, ITEM)


def test_found_behind_comes_after_even_when_dated_later() -> None:
    events = {"m": event("m", 5), "b": event("b", 9), "a": event("a", 3), "c": event("c", 3)}
    newer = {"m": set(), "b": {"m"}, "a": {"m"}, "c": {"a", "gone"}}
    assert [e.commit.sha for e in history_order(events, newer) if e.commit] == ["m", "b", "a", "c"]


def test_same_date_keeps_the_order_found() -> None:
    events = {"x": event("x", 1), "y": event("y", 1)}
    assert [e.commit.sha for e in history_order(events, {"x": set(), "y": set()}) if e.commit] == [
        "x",
        "y",
    ]
