from tadu.codex_hook_output import codex_hook_output


def test_unsupported_events_are_silent() -> None:
    assert codex_hook_output({"hook_event_name": "Stop"}) is None
