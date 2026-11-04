from pathlib import Path

from card_samples import sample_card

from tadu.build_cards import build_cards
from tadu.local_config import LocalConfig
from tadu.project_entry import ProjectEntry
from tadu.repository_entry import RepositoryEntry


def test_with_context() -> None:
    item = sample_card().item
    entry = RepositoryEntry("shop", "git@github.com:acme/shop.git")
    project = ProjectEntry(
        "storefront", "Store", ("shop",), (("client", "acme"), ("agency", "studio"))
    )
    local = LocalConfig({}, None, "ed://{path}:{line}")
    (card,) = build_cards((item,), "shop", Path("/w"), entry, project, local)
    assert card.column == "ready"
    assert card.project == "storefront"
    assert card.organizations == (("client", "acme"), ("agency", "studio"))
    assert card.editor_url == "ed:///w/TODO.md:2"
    assert card.remote_url == "https://github.com/acme/shop/blob/HEAD/TODO.md#L2"


def test_column_follows_queue() -> None:
    (card,) = build_cards((sample_card().item,), "shop", Path("/w"), None, None, None)
    assert card.column == "ready"


def test_without_context() -> None:
    (card,) = build_cards((sample_card().item,), "shop", Path("/w"), None, None, None)
    assert (card.project, card.organizations) == (None, ())
    assert (card.editor_url, card.remote_url) == (None, None)
