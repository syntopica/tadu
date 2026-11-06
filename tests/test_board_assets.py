import re
from importlib.resources import files

from tadu.board_asset import board_asset
from tadu.board_asset_name_pattern import BOARD_ASSET_NAME_PATTERN

BOARD = files("tadu") / "board"
SCRIPTS = sorted(p.name for p in BOARD.iterdir() if p.name.endswith(".js"))
IMPORT = re.compile(r'^import \{ (\w+) \} from "\./([a-z0-9-]+\.js)";$', re.MULTILINE)


def text(name: str) -> str:
    asset = board_asset(name)
    assert asset is not None
    return asset[0].decode()


def every_script() -> str:
    return "\n".join(text(name) for name in SCRIPTS)


def test_every_file_is_served() -> None:
    assert len(SCRIPTS) > 50
    for path in BOARD.iterdir():
        assert BOARD_ASSET_NAME_PATTERN.fullmatch(path.name), path.name


def test_page_assets_never_inject_html() -> None:
    for name in ("index.html", *SCRIPTS):
        source = text(name)
        for banned in ("innerHTML", "outerHTML", "insertAdjacentHTML", "document.write", "eval("):
            assert banned not in source, name
        assert "new Function" not in source, name
        assert 'setAttribute("style"' not in source, name


def test_index_has_one_module_script_and_no_inline_style() -> None:
    page = text("index.html")
    assert re.findall(r"<script\b([^>]*)>(.*?)</script>", page, re.DOTALL) == [
        (' type="module" src="/app.js"', ""),
    ]
    assert "style=" not in page
    assert "<style" not in page
    assert '<link rel="stylesheet" href="/board.css">' in page


def test_modules_export_one_unit_and_import_only_siblings() -> None:
    for name in SCRIPTS:
        source = text(name)
        assert len(re.findall(r"^export ", source, re.MULTILINE)) == 1, name
        imports = re.findall(r"^import .*$", source, re.MULTILINE)
        assert len(imports) == len(IMPORT.findall(source)), name
        for unit, module in IMPORT.findall(source):
            assert re.search(
                rf"^export (async )?(function|const) {unit}\b", text(module), re.MULTILINE
            )


def test_no_external_resources() -> None:
    page = text("index.html")
    assert all(url.startswith("/") for url in re.findall(r'(?:src|href)="([^"]*)"', page))
    style = text("board.css")
    assert "url(" not in style
    assert "@import" not in style
    scripts = every_script()
    assert re.findall(r"fetch\(([^,)]*)", scripts) == ['"/api/cards"']
    assert "XMLHttpRequest" not in scripts
    assert "WebSocket" not in scripts
    assert "sendBeacon" not in scripts


def test_links_are_checked_and_isolated() -> None:
    scripts = every_script()
    for needed in ("https://", "javascript:", "data:", "vbscript:", "noopener noreferrer"):
        assert needed in scripts
    assert "_blank" in scripts
    assert "textContent" in scripts
    assert '"X-Tadu-Token": token' in scripts
    assert "sessionStorage" in scripts
    assert 'replaceState(null, "", "/")' in scripts
    assert "cookie" not in scripts.lower()
    assert "anchor.href = url" in text("external-link.js")
    assert 'anchor.rel = "noopener noreferrer"' in text("external-link.js")
    assert "safeEditor(card.editor_url" in text("detail-actions.js")
    assert "safeRemote(card.remote_url" in text("detail-actions.js")


def test_card_title_is_clamped_and_carries_the_full_text() -> None:
    style = text("board.css")
    for rule in ("-webkit-line-clamp: 2", "line-clamp: 2", "-webkit-box-orient: vertical"):
        assert rule in style
    assert "title.title = card.title" in text("board-card.js")
    assert "title.title = card.title" in text("list-row.js")
