from tadu.derived_key import derived_key
from tadu.id_targets import id_targets

UID = "t-55161023-f3a9-43a3-94df-589ca752fa13"
LINES = [
    "- [ ] a",
    "",
    "  ID: t-55161023-f3a9-43a3-94df-589ca752fa13",
    "- [ ] b",
    "- [~] c",
    "- [x] d",
]


def test_every_open_item_without_an_id() -> None:
    assert id_targets(LINES, "repo", None) == [3, 4]


def test_one_item_by_derived_key() -> None:
    assert id_targets(LINES, "repo", derived_key("repo", "TODO.md", "b", 0)) == [3]


def test_unknown_key_is_refused() -> None:
    assert id_targets(LINES, "repo", "k-0") == "no open item has key k-0"


def test_item_with_an_id_is_refused() -> None:
    assert id_targets(LINES, "repo", UID) == f"the item with key {UID} already has an ID"


def test_invalid_id_counts_as_present() -> None:
    lines = ["- [ ] a", "", "  ID: bad"]
    assert id_targets(lines, "repo", None) == []
    key = derived_key("repo", "TODO.md", "a", 0)
    assert id_targets(lines, "repo", key) == f"the item with key {key} already has an ID"
