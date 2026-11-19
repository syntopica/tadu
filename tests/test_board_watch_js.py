"""The page keeps checking, lightly, that it may show what it shows: an ended session
leaves for the sign-in page, a board that stops answering clears the page until it
answers again, then the page reloads.
"""

from watch_js import run

SCENARIOS = {
    "ok": """
const next = await tick({ status: 200, body: { ok: true } });
out({ firstWait, next, log, requests, left: store.left });
""",
    "signed_out": """
const next = await tick({ status: 401, body: { error: "signed out" } });
out({ next, log, left: store.left, payload: store.payload });
""",
    "proxy_401": """
const next = await tick({ status: 401 });
out({ next, log, left: store.left });
""",
    "down_then_back": """
const waits = [await tick("offline")];
const afterOne = log.slice();
waits.push(await tick({ status: 502 }));
const afterTwo = log.slice();
waits.push(await tick("offline"));
const afterThree = log.slice();
waits.push(await tick({ status: 200, body: { ok: true } }));
out({ waits, afterOne, afterTwo, afterThree, log, title: document.title, left: store.left });
""",
    "down_then_signed_out": """
await tick("offline");
await tick("offline");
const next = await tick({ status: 401, body: { error: "signed out" } });
out({ next, log });
""",
    "hidden": """
document.visibilityState = "hidden";
const whileHidden = await tick({ status: 200 });
const asked = requests.length;
document.visibilityState = "visible";
answers = [{ status: 401, body: { error: "signed out" } }];
await listeners.visibilitychange();
out({ whileHidden, asked, log, requests: requests.length });
""",
    "online_and_busy": """
answers = [{ status: 200 }, { status: 200 }];
await Promise.all([listeners.online(), check()]);
out({ requests: requests.length, timers: timers.length });
""",
}


def test_a_passed_check_changes_nothing_and_checks_again_later() -> None:
    result = run(SCENARIOS["ok"])
    assert (result["firstWait"], result["next"]) == (30_000, 30_000)
    assert result["log"] == []
    assert result["requests"] == [["api/session", {}, "GET"]]
    assert result["left"] is False
    assert run(SCENARIOS["ok"], with_token=True)["requests"] == [
        ["api/session", {"X-Tadu-Token": "t1"}, "GET"]
    ]


def test_an_ended_session_empties_the_page_and_leaves() -> None:
    result = run(SCENARIOS["signed_out"])
    assert result["next"] is None
    assert result["log"] == ["emptied", "reload"]
    assert (result["left"], result["payload"]) == (True, None)


def test_a_401_that_is_not_the_boards_counts_as_down() -> None:
    result = run(SCENARIOS["proxy_401"])
    assert (result["next"], result["log"], result["left"]) == (5_000, [], False)


def test_a_board_down_clears_the_page_until_it_answers_then_reloads() -> None:
    result = run(SCENARIOS["down_then_back"])
    assert result["waits"] == [5_000, 5_000, 5_000, None]
    assert result["afterOne"] == []  # one failure may be a blip
    shown = (
        "shown: The board cannot be reached Nothing of it is shown until it answers again. "
        "This page reloads by itself when it does."
    )
    assert result["afterTwo"] == ["emptied", shown]
    assert result["afterThree"] == result["afterTwo"]  # cleared once
    assert result["log"] == ["emptied", shown, "reload"]
    assert result["title"] == "Unreachable · tadu"
    assert result["left"] is True


def test_back_up_but_signed_out_leaves_for_the_sign_in_page() -> None:
    result = run(SCENARIOS["down_then_signed_out"])
    assert result["next"] is None
    log = result["log"]
    assert isinstance(log, list)
    assert log[-2:] == ["emptied", "reload"]


def test_a_hidden_page_does_not_check_and_checks_when_shown_again() -> None:
    result = run(SCENARIOS["hidden"])
    assert (result["whileHidden"], result["asked"]) == (None, 0)
    assert result["requests"] == 1
    assert result["log"] == ["emptied", "reload"]


def test_checks_do_not_overlap() -> None:
    assert run(SCENARIOS["online_and_busy"]) == {"requests": 1, "timers": 2}


def test_a_token_board_refusing_its_token_leaves() -> None:
    refused = SCENARIOS["signed_out"].replace(
        '{ status: 401, body: { error: "signed out" } }', "{ status: 403 }"
    )
    assert run(refused, with_token=True)["log"] == ["emptied", "reload"]
    # Without a token, a 403 is not the board's refusing it: it counts as down.
    assert run(refused)["log"] == []
