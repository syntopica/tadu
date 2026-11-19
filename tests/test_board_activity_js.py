"""Acting on an open board (pressing, typing, scrolling) is activity: the next check
says so, which keeps the session alive; a page left alone is not.
"""

from watch_js import run

SETUP = """
const ok = (remaining) => ({ status: 200, body: { ok: true, remaining, warn: 300 } });
const methods = () => requests.map(([, , method]) => method);
const act = (name = "pointerdown") => listeners[name]();
"""


def test_the_activity_events_are_pressing_typing_and_scrolling() -> None:
    result = run(SETUP + "out({ events: Object.keys(listeners).sort() });")
    assert result["events"] == [
        "keydown",
        "online",
        "pointerdown",
        "stay-signed-in:click",
        "touchstart",
        "visibilitychange",
        "wheel",
    ]


def test_a_check_after_activity_reports_it_and_one_without_does_not() -> None:
    result = run(
        SETUP
        + """
await tick(ok(3600));  // the first check learns the page has a session
act();
await tick(ok(3600));
await tick(ok(3600));
act("keydown");
act("wheel");
await tick(ok(3600));
out({ methods: methods() });
"""
    )
    assert result == {"methods": ["GET", "POST", "GET", "POST"]}


def test_activity_before_the_first_answer_waits_for_it() -> None:
    # The page has just loaded the board, which counted as use already.
    result = run(
        SETUP + "act(); await tick(ok(3600)); await tick(ok(3600)); out({ m: methods() });"
    )
    assert result == {"m": ["GET", "POST"]}


def test_a_token_board_has_no_session_to_keep_alive() -> None:
    result = run(
        SETUP
        + """
await tick({ status: 200, body: { ok: true } });
act();
await tick({ status: 200, body: { ok: true } });
out({ m: methods() });
""",
        with_token=True,
    )
    assert result == {"m": ["GET", "GET"]}


def test_activity_during_the_warning_answers_it_at_once() -> None:
    result = run(
        SETUP
        + """
await tick(ok(200));
const warned = document.getElementById("session-warning").hidden;
answers = [ok(600)];
act("keydown");
await new Promise((resolve) => setTimeout(resolve, 10));
out({ warned, methods: methods(), hidden: document.getElementById("session-warning").hidden });
"""
    )
    assert result == {"warned": False, "methods": ["GET", "POST"], "hidden": True}


def test_activity_while_a_check_is_out_answers_the_warning_right_after() -> None:
    result = run(
        SETUP
        + """
await tick(ok(200));  // warned
answers = [ok(190)];
const out1 = check();  // a check goes out
act();  // busy: this activity waits for it
await out1;
out({ methods: methods(), next: timers.at(-1).ms });
"""
    )
    assert result == {"methods": ["GET", "GET"], "next": 0}
