from tadu.log_view import LogView


def test_view_holds_its_parts() -> None:
    view = LogView(["## 2026"], [False], [(0, 2, "2026")])
    assert view.headings == [(0, 2, "2026")]
