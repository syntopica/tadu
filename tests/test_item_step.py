from tadu.file_versions import FileVersions
from tadu.item_step import item_step

A, A2, A3 = "- [ ] Fix login.", "- [~] Fix login.", "- [!] Fix login.\n\n  Waiting on IT."


def step(before: tuple[str, ...], after: str, texts: set[str]) -> tuple[object, set[str]]:
    """(before and after texts or None, the texts to look for next), all in TODO.md."""
    where = frozenset(("TODO.md", text) for text in texts)
    found, rest = item_step((FileVersions("TODO.md", before, after),), where, "shop")
    pair = None if found is None else (found[0].text if found[0] else None, found[1].text)
    assert {path for path, _ in rest} <= {"TODO.md"}
    return pair, {text for _, text in rest}


def test_change_that_does_not_hold_the_item() -> None:
    assert step(("- [ ] B.",), "- [ ] C.", {A}) == (None, {A})


def test_item_unchanged_while_others_changed() -> None:
    assert step((f"{A}\n- [ ] B.",), A, {A}) == (None, {A})


def test_changed() -> None:
    assert step((A,), A2, {A2}) == ((A, A2), {A})


def test_created() -> None:
    assert step(("",), A, {A}) == ((None, A), set())


def test_held_only_inside_a_fence() -> None:
    fenced = f"```\n{A}\n```"
    assert step(("",), fenced, {A}) == (None, {A})


def test_merge_that_took_one_side() -> None:
    assert step((A, A2), A2, {A2}) == (None, {A2})


def test_merge_unlike_every_parent() -> None:
    assert step((A2, A3), "- [!] Fix login.", {"- [!] Fix login."}) == (
        (A2, "- [!] Fix login."),
        {A2, A3},
    )


def test_merge_where_the_first_parent_lacked_it() -> None:
    assert step(("", A), A2, {A2}) == ((A, A2), {A})


def test_only_the_file_the_item_is_in() -> None:
    versions = (FileVersions("TODO_LOG.md", ("",), A),)
    assert item_step(versions, frozenset({("TODO.md", A)}), "shop") == (
        None,
        frozenset({("TODO.md", A)}),
    )
