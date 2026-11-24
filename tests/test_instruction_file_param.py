import pytest

from tadu.cli import main


@pytest.mark.parametrize("command", ["init", "sync"])
def test_help_names_the_instruction_discovery_order(
    command: str, capsys: pytest.CaptureFixture[str]
) -> None:
    with pytest.raises(SystemExit, match="0"):
        main([command, "--help"])
    help_text = capsys.readouterr().out
    assert "AGENTS.override.md" in help_text
    assert "CLAUDE.md" in help_text
