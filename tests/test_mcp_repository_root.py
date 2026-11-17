import re
from pathlib import Path

import pytest

from tadu.mcp_repository_root import mcp_repository_root
from tadu.mcp_scope import McpScope
from tadu.workspace_error import WorkspaceError


def twins(tmp_path: Path) -> tuple[Path, Path, McpScope]:
    acme, globex = tmp_path / "acme" / "api", tmp_path / "globex" / "api"
    return acme, globex, McpScope((str(acme), str(globex)), None)


def test_a_shared_folder_name_never_picks_one(tmp_path: Path) -> None:
    acme, globex, scope = twins(tmp_path)
    listing = f"give `repository` as one of: {acme}; {globex}"
    with pytest.raises(WorkspaceError, match=f"^several repositories; {re.escape(listing)}$"):
        mcp_repository_root(scope, None)
    with pytest.raises(WorkspaceError, match=r"^no repository api; give"):
        mcp_repository_root(scope, "api")


def test_the_full_path_picks_exactly_one(tmp_path: Path) -> None:
    acme, globex, scope = twins(tmp_path)
    assert mcp_repository_root(scope, str(globex)) == str(globex)
    assert mcp_repository_root(scope, f"{globex}/") == str(globex)
    assert mcp_repository_root(scope, f"{acme}/../api") == str(acme)


def test_a_relative_path_is_never_guessed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    acme, _globex, scope = twins(tmp_path)
    acme.mkdir(parents=True)
    monkeypatch.chdir(acme.parent)
    with pytest.raises(WorkspaceError, match="no repository api"):
        mcp_repository_root(scope, "api")
    with pytest.raises(WorkspaceError, match=re.escape("no repository ./api")):
        mcp_repository_root(scope, "./api")


def test_unique_names_and_one_folder_given_twice(tmp_path: Path) -> None:
    shop, api = tmp_path / "shop", tmp_path / "api"
    assert mcp_repository_root(McpScope((str(shop), str(api)), None), "shop") == str(shop)
    assert mcp_repository_root(McpScope((str(api), f"{api}/."), None), None) == str(api)
    with pytest.raises(WorkspaceError, match=re.escape(f"one of: shop ({shop}); api ({api})")):
        mcp_repository_root(McpScope((str(shop), str(api)), None), "nope")


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
    scope = McpScope((), str(tmp_path))
    acme_docs, globex = tmp_path / "acme" / "api" / "docs", tmp_path / "globex" / "api"
    assert mcp_repository_root(scope, "acme-api") == str(acme_docs)
    assert mcp_repository_root(scope, str(globex)) == str(globex)
    with pytest.raises(WorkspaceError, match=r"^several repositories"):
        mcp_repository_root(scope, None)
    with pytest.raises(WorkspaceError, match="no repository gone"):
        mcp_repository_root(scope, "gone")
    (tmp_path / "tadu-workspace.toml").write_text('version = 1\n[[repository]]\nkey = "acme-api"\n')
    (tmp_path / "tadu-workspace.local.toml").write_text(
        'version = 1\n[paths]\nacme-api = "acme/api"\n'
    )
    assert mcp_repository_root(scope, None) == str(tmp_path / "acme" / "api")
