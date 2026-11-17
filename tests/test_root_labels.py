from pathlib import Path

from tadu.root_labels import root_labels


def test_unique_names_stay_short(tmp_path: Path) -> None:
    shop, api = tmp_path / "shop", tmp_path / "acme" / "api"
    assert root_labels((str(shop), str(api))) == {"shop": shop, "api": api}


def test_shared_names_use_the_full_path(tmp_path: Path) -> None:
    acme, globex, shop = tmp_path / "acme" / "api", tmp_path / "globex" / "api", tmp_path / "shop"
    assert root_labels((str(acme), str(shop), str(globex))) == {
        str(acme): acme,
        "shop": shop,
        str(globex): globex,
    }


def test_one_folder_given_twice_is_one_root(tmp_path: Path) -> None:
    api = tmp_path / "api"
    assert root_labels((str(api), f"{api}/.", f"{tmp_path}/x/../api/")) == {"api": api}
