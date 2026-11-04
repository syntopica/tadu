import re

from tadu.board_asset import board_asset


def text(name: str) -> str:
    asset = board_asset(name)
    assert asset is not None
    return asset[0].decode()


def test_page_assets_never_inject_html() -> None:
    for name in ("index.html", "filters.js", "board.js"):
        source = text(name)
        for banned in ("innerHTML", "outerHTML", "insertAdjacentHTML", "document.write", "eval("):
            assert banned not in source


def test_index_has_no_inline_script_or_style() -> None:
    page = text("index.html")
    assert re.findall(r"<script\b([^>]*)>(.*?)</script>", page, re.DOTALL) == [
        (' src="/filters.js" defer', ""),
        (' src="/board.js" defer', ""),
    ]
    assert "style=" not in page
    assert "<style" not in page
    assert '<link rel="stylesheet" href="/board.css">' in page


def test_no_external_resources() -> None:
    page = text("index.html")
    assert all(url.startswith("/") for url in re.findall(r'(?:src|href)="([^"]*)"', page))
    style = text("board.css")
    assert "url(" not in style
    assert "@import" not in style
    assert re.findall(r"fetch\(([^,)]*)", text("board.js")) == ['"/api/cards"']


def test_links_are_checked_and_isolated() -> None:
    script = text("board.js")
    for needed in ("https://", "javascript:", "data:", "vbscript:", "noopener noreferrer"):
        assert needed in script
    assert "_blank" in script
    assert "textContent" in script
    assert "/api/cards" in script
    assert '"X-Tadu-Token": token' in script
    assert "sessionStorage" in script
    assert 'replaceState(null, "", "/")' in script
    assert "cookie" not in script.lower()


def test_filters_and_cancelled_toggle_present() -> None:
    page = text("index.html")
    for control in ("repository", "project", "organization", "role", "assignee", "priority"):
        assert f'id="filter-{control}"' in page
    assert 'id="filter-label"' in page
    assert 'id="waiting-on-me"' in page
    assert 'id="show-cancelled"' in page
