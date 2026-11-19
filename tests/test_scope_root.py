import re
from dataclasses import replace
from pathlib import Path

import pytest

from tadu.scope import Scope
from tadu.scope_root import scope_root
from tadu.workspace_error import WorkspaceError


def root(scope: Scope, repository: str | None) -> str:
    return str(scope_root(replace(scope, repository=repository))[1])


def twins(tmp_path: Path) -> tuple[Path, Path, Scope]:
    acme, globex = tmp_path / "acme" / "api", tmp_path / "globex" / "api"
    return acme, globex, Scope((str(acme), str(globex)))


def test_a_shared_folder_name_never_picks_one(tmp_path: Path) -> None:
    acme, globex, scope = twins(tmp_path)
    listing = f"give --repository as one of: {acme}; {globex}"
    with pytest.raises(WorkspaceError, match=f"^several repositories; {re.escape(listing)}$"):
        root(scope, None)
    with pytest.raises(WorkspaceError, match=r"^no repository api; give"):
        root(scope, "api")


def test_the_full_path_picks_exactly_one(tmp_path: Path) -> None:
    acme, globex, scope = twins(tmp_path)
    assert root(scope, str(globex)) == str(globex)
    assert root(scope, f"{globex}/") == str(globex)
    assert root(scope, f"{acme}/../api") == str(acme)


def test_a_relative_path_is_never_guessed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    acme, _globex, scope = twins(tmp_path)
    acme.mkdir(parents=True)
    monkeypatch.chdir(acme.parent)
    with pytest.raises(WorkspaceError, match="no repository api"):
        root(scope, "api")
    with pytest.raises(WorkspaceError, match=re.escape("no repository ./api")):
        root(scope, "./api")


def test_unique_names_and_one_folder_given_twice(tmp_path: Path) -> None:
    shop, api = tmp_path / "shop", tmp_path / "api"
    assert root(Scope((str(shop), str(api))), "shop") == str(shop)
    assert root(Scope((str(api), f"{api}/.")), None) == str(api)
    with pytest.raises(WorkspaceError, match=re.escape(f"one of: shop ({shop}); api ({api})")):
        root(Scope((str(shop), str(api))), "nope")


def test_workspace_keys_and_paths(tmp_path: Path) -> None:
    for client in ("acme", "globex"):
        (tmp_path / client / "api").mkdir(parents=True)
    (tmp_path / "tadu-workspace.toml").write_text(
        'version = 1\n[[repository]]\nkey = "acme-api"\nbacklog = "docs"\n'
        '[[repository]]\nkey = "globex-api"\n[[repository]]\nkey = "gone"\n'
    )
    (tmp_path / "tadu-workspace.local.toml").write_text(
        'version = 1\n[paths]\nacme-api = "acme/api"\nglobex-api = "globex/api"\n'
    )
    scope = Scope((), str(tmp_path))
    acme_docs, globex = tmp_path / "acme" / "api" / "docs", tmp_path / "globex" / "api"
    assert root(scope, "acme-api") == str(acme_docs)
    assert root(scope, str(globex)) == str(globex)
    with pytest.raises(WorkspaceError, match=r"^several repositories"):
        root(scope, None)
    with pytest.raises(WorkspaceError, match="no repository gone"):
        root(scope, "gone")
    (tmp_path / "tadu-workspace.toml").write_text('version = 1\n[[repository]]\nkey = "acme-api"\n')
    (tmp_path / "tadu-workspace.local.toml").write_text(
        'version = 1\n[paths]\nacme-api = "acme/api"\n'
    )
    assert root(scope, None) == str(tmp_path / "acme" / "api")


def test_the_label_comes_with_the_root(tmp_path: Path) -> None:
    shop, api = tmp_path / "shop", tmp_path / "api"
    scope = Scope((str(shop), str(api)), repository=str(api))
    assert scope_root(scope) == ("api", api)
    assert scope_root(Scope((str(shop),))) == ("shop", shop)
