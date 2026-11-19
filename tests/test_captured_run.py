import pytest

from tadu.captured_run import captured_run
from tadu.cli import main


def test_output_errors_and_argparse_exits(capsys: pytest.CaptureFixture[str]) -> None:
    code, out, err = captured_run(main, ["list", "--kind", "soon"])
    assert (code, out) == (2, "")
    assert "invalid choice: 'soon'" in err
    assert captured_run(main, ["--version"])[0] == 0

    def exit_with_text(_argv: list[str]) -> int:
        message = "stop"
        raise SystemExit(message)

    assert captured_run(exit_with_text, []) == (2, "", "")
    assert capsys.readouterr() == ("", "")


def test_an_unexpected_failure_is_reported_not_raised() -> None:
    def broken(_argv: list[str]) -> int:
        message = "boom"
        raise ValueError(message)

    code, out, err = captured_run(broken, ["set"])
    assert (code, out) == (70, "")
    assert err.startswith("tadu set: internal error\nTraceback")
    assert "ValueError: boom" in err
    assert captured_run(broken, [])[2].startswith("tadu: internal error")
