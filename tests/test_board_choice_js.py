import json

import pytest
from board_js import board_js

VALUES = ["shop", "shop-admin", "Blog", "agents", "atrium"]
TYPED = ["", "  ", "shop", " shop ", "blog", "BLOG", "admin", "a", "nothing", "shop-"]
SCRIPT = """
const { resolveChoice } = await load("resolve-choice.js");
const { restoreDrill } = await load("restore-drill.js");
const [values, typed] = ARGS;
const before = { filters: { role: "" }, text: "fix", scope: "mine", where: { company: "pp" } };
const drilled = {
  filters: { role: "client" }, text: "", scope: "all", where: { company: "x" }, beforeDrill: before,
};
restoreDrill(drilled);
const untouched = { filters: { role: "x" }, text: "t", scope: "all", where: {}, beforeDrill: null };
restoreDrill(untouched);
const twice = { ...drilled, filters: { role: "other" } };
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
        "filters": {"role": ""},
        "text": "fix",
        "scope": "mine",
        "where": {"company": "pp"},
        "beforeDrill": None,
    }
    assert results["untouched"] == {
        "filters": {"role": "x"},
        "text": "t",
        "scope": "all",
        "where": {},
        "beforeDrill": None,
    }
    assert results["twice"] == {"role": "other"}
