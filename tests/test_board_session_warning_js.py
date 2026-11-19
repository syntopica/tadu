"""A session about to end for lack of use is warned about, with a countdown, in time;
Stay signed in uses the board to push the end back, and the warning goes.
"""

from watch_js import run

AHEAD = """
const ok = (remaining) => ({ status: 200, body: { ok: true, remaining, warn: 300 } });
const banner = () => [
  document.getElementById("session-warning").hidden,
  document.getElementById("session-warning-text").textContent,
];
"""


def test_far_from_the_end_no_warning_and_the_usual_wait() -> None:
    result = run(AHEAD + "out({ next: await tick(ok(3600)), banner: banner() });")
    assert result == {"next": 30_000, "banner": [True, ""]}


def test_the_next_check_comes_when_the_warning_is_due() -> None:
    result = run(AHEAD + "out({ next: await tick(ok(310)), banner: banner() });")
    assert result == {"next": 10_000, "banner": [True, ""]}


def test_within_the_warning_time_a_countdown_shows_each_second() -> None:
    result = run(
        AHEAD
        + """
const next = await tick(ok(200));
const first = banner();
now += 20_000;
tickers.at(-1).run();
const later = banner();
now += 200_000;
tickers.at(-1).run();
out({ next, first, later, end: banner(), every: tickers.at(-1).ms });
"""
    )
    assert result["next"] == 30_000
    assert result["first"] == [False, "You will be signed out in 3:20 for inactivity."]
    assert result["later"] == [False, "You will be signed out in 3:00 for inactivity."]
    assert result["end"] == [False, "You will be signed out in 0:00 for inactivity."]
    assert result["every"] == 1000


def test_close_to_the_end_it_checks_just_after_it() -> None:
    result = run(AHEAD + "out({ next: await tick(ok(20)) });")
    assert result == {"next": 21_000}


def test_used_elsewhere_the_warning_goes() -> None:
    result = run(
        AHEAD
        + """
await tick(ok(200));
const shown = banner()[0];
const next = await tick(ok(14 * 86400));
out({ shown, hidden: banner()[0], next, stopped: tickers.at(-1).stopped ?? false });
"""
    )
    assert result == {"shown": False, "hidden": True, "next": 30_000, "stopped": True}


def test_stay_signed_in_reports_activity_at_once() -> None:
    result = run(
        AHEAD
        + """
await tick(ok(200));
answers = [ok(600)];
listeners["stay-signed-in:click"]();
await new Promise((resolve) => setTimeout(resolve, 10));
out({ asked: requests.map(([url, , method]) => `${method} ${url}`), hidden: banner()[0] });
"""
    )
    assert result == {"asked": ["GET api/session", "POST api/session"], "hidden": True}


def test_a_token_board_has_no_session_to_warn_about() -> None:
    result = run(
        AHEAD + "out({ next: await tick({ status: 200, body: { ok: true } }), banner: banner() });",
        with_token=True,
    )
    assert result == {"next": 30_000, "banner": [True, ""]}


def test_the_countdown_stops_once_the_page_is_emptied() -> None:
    result = run(
        AHEAD
        + """
await tick(ok(200));
document.getElementById = () => null;
tickers.at(-1).run();
out({ stopped: tickers.at(-1).stopped ?? false });
"""
    )
    assert result == {"stopped": True}
