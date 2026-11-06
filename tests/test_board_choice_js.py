import json

import pytest
from board_js import board_js

VALUES = ["shop", "shop-admin", "Blog", "agents", "atrium"]
TYPED = ["", "  ", "shop", " shop ", "blog", "BLOG", "admin", "a", "nothing", "shop-"]
SCRIPT = """
const { resolveChoice } = await load("resolve-choice.js");
const { restoreDrill } = await load("restore-drill.js");
const [values, typed] = ARGS;
const before = { filters: { repository: "" }, text: "fix", scope: "mine" };
const drilled = {
  filters: { repository: "shop" }, text: "", scope: "all", beforeDrill: before,
};
restoreDrill(drilled);
const untouched = { filters: { repository: "x" }, text: "t", scope: "all", beforeDrill: null };
restoreDrill(untouched);
const twice = { ...drilled, filters: { repository: "other" } };
restoreDrill(twice);
out({
  choices: typed.map((text) => resolveChoice(text, values)),
  drilled,
  untouched,
  twice: twice.filters,
});
"""


@pytest.fixture(scope="module")
def results() -> dict[str, object]:
    result = board_js(SCRIPT.replace("ARGS", json.dumps([VALUES, TYPED])))
    assert isinstance(result, dict)
    return result


def test_typed_text_names_one_value_or_none(results: dict[str, object]) -> None:
    assert results["choices"] == [
        "",
        "",
        "shop",
        "shop",
        "Blog",
        "Blog",
        "shop-admin",
        None,
        None,
        "shop-admin",
    ]


def test_returning_to_portfolio_restores_what_the_drill_down_replaced(
    results: dict[str, object],
) -> None:
    assert results["drilled"] == {
        "filters": {"repository": ""},
        "text": "fix",
        "scope": "mine",
        "beforeDrill": None,
    }
    assert results["untouched"] == {
        "filters": {"repository": "x"},
        "text": "t",
        "scope": "all",
        "beforeDrill": None,
    }
    assert results["twice"] == {"repository": "other"}
