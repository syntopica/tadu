import pytest

from tadu.secret_lines import secret_lines

SAMPLES = {
    "a private key block": "-----BEGIN OPENSSH PRIVATE KEY-----",
    "an AWS access key id": "id " + "AKIA" + "Q7XJ" * 4,
    "a GitHub token": "ghp_" + "a1" * 18,
    "a Slack token": "xoxb-" + "1234567890ab",
    "an OpenAI or Anthropic API key": "sk-ant-" + "a1b2" * 6,
    "a Stripe secret key": "sk_live_" + "a1b2" * 5,
    "a Google API key": "AIza" + "a" * 35,
    "a JSON web token": "eyJ" + "a" * 10 + ".eyJ" + "b" * 10 + "." + "c" * 10,
    "a credential assignment": "PASSWORD = " + "hunter2hunter2hunter2",
}


@pytest.mark.parametrize(("kind", "line"), SAMPLES.items())
def test_each_kind_is_found_on_its_line(kind: str, line: str) -> None:
    assert secret_lines(f"first line\n{line}\n") == ((2, kind),)


def test_plain_text_has_none() -> None:
    assert secret_lines("Fix the Safari crash in the toolbar\nDone when: CI is green.") == ()


def test_a_hint_word_alone_is_not_a_secret() -> None:
    assert secret_lines("Rotate the API token after the release") == ()
