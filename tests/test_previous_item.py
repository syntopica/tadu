from tadu.file_versions import FileVersions
from tadu.markdown_items import markdown_items
from tadu.previous_item import previous_item

ID = "t-3f2a1b4c-5d6e-4f70-8a91-b2c3d4e5f607"
OTHER = "t-55161023-f3a9-43a3-94df-589ca752fa13"


def find(before: str, after: str, log_before: str = "", log_after: str = "") -> str | None:
    """The text previous_item finds for the last item of the new TODO.md, else of the log."""
    versions = (
        FileVersions("TODO.md", (before,), after),
        FileVersions("TODO_LOG.md", (log_before,), log_after),
    )
    new = (
        markdown_items(log_after, "shop", "TODO_LOG.md") or markdown_items(after, "shop", "TODO.md")
    )[-1]
    old = previous_item(versions, 0, new, "shop")
    return old.text if old else None


def test_same_text_in_another_file() -> None:
    assert find("- [ ] A.", "", "", "- [ ] A.") == "- [ ] A."


def test_same_id_however_changed() -> None:
    old = f"- [ ] Old words.\n\n  ID: {ID}"
    assert find(old, f"- [~] New.\n\n  ID: {ID}") == old


def test_closing_re_keys_the_item() -> None:
    log = "- [x] 2026-11-01 — **Backend:** Fix login.\n  - Result: Fixed.\n  - Evidence: CI."
    assert find("- [ ] Fix login\n- [ ] Other.", "- [ ] Other.", "", log) == "- [ ] Fix login"


def test_an_unchanged_item_is_never_taken() -> None:
    assert find("- [ ] Fix login.", "- [ ] Fix login.\n- [ ] Fix login now.") is None


def test_another_id_is_never_taken() -> None:
    old = f"- [ ] Fix login.\n\n  ID: {OTHER}"
    assert find(old, f"- [ ] Fix login.\n\n  ID: {ID}") is None


def test_an_id_added_later() -> None:
    assert find("- [ ] Fix login.", f"- [ ] Fix login.\n\n  ID: {ID}") == "- [ ] Fix login."


def test_too_different_is_new() -> None:
    assert find("- [ ] Fix login.", "- [ ] Ship the CSV export.") is None
