from pathlib import Path

import pytest

from tadu.secret_lines import secret_lines
from tadu.secret_patterns import SECRET_PATTERNS

ROOT = Path(__file__).parent.parent
SAMPLES = {
    "a private key block": "-----BEGIN OPENSSH PRIVATE KEY-----",
    "an AWS access key id": "id " + "AKIA" + "Q7XJ" * 4,
    "a GitHub token": "ghp_" + "a1" * 18,
    "a Slack token": "xoxb-" + "1234567890ab",
    "an OpenAI or Anthropic API key": "sk-ant-" + "a1b2" * 6,
    "a Stripe secret key": "sk_live_" + "a1b2" * 5,
    "a Google API key": "AIza" + "a" * 35,
    "a JSON web token": "eyJ" + "a" * 10 + ".eyJ" + "b" * 10 + "." + "c" * 10,
    "a GitLab token": "glpat-" + "aB3_" * 5,
    "an npm token": "npm_" + "aB3d" * 9,
    "a PyPI token": "pypi-AgEIcHlwaS5vcmc" + "aB3_" * 13,
    "a SendGrid key": "SG." + "aB3d" * 5 + "aB." + "aB3d" * 10 + "aB3",
    "a Shopify token": "shpat_" + "a1b2" * 8,
    "a Square token": "sq0atp-" + "aB3_" * 6,
    "a Mailchimp key": "a1b2" * 8 + "-us12",
    "a Twilio key": "SK" + "a1b2" * 8,
    "an Azure storage key": "AccountName=acme;AccountKey=" + "aB3+" * 21 + "==",
    "a password in a URL": "https://deploy:s3cretPass@git.example.com/acme/shop.git",
    "a credential assignment": "PASSWORD = " + "hunter2hunter2hunter2",
}


@pytest.mark.parametrize(("kind", "line"), SAMPLES.items())
def test_each_kind_is_found_on_its_line(kind: str, line: str) -> None:
    assert secret_lines(f"first line\n{line}\n") == ((2, kind),)


def test_every_kind_has_a_sample_and_hints_its_matches_hold() -> None:
    assert [kind for kind, _, _ in SECRET_PATTERNS] == list(SAMPLES)
    for kind, hints, pattern in SECRET_PATTERNS:
        match = pattern.search(SAMPLES[kind])
        assert match is not None, kind
        assert all(hint == hint.lower() for hint in hints), kind
        assert any(hint in match.group(0).lower() for hint in hints), kind


@pytest.mark.parametrize(
    "line",
    [
        "aws_secret_access_key = wJalrXUtnFEMI2K7MDENGbPxRfiCYEXAMPLEKEY",
        "export GITHUB_API_KEY=ghx0" + "a1b2c3d4" * 3,
        "auth_token: 3f9a" + "b" * 20,
    ],
)
def test_credential_names_with_prefixes_count(line: str) -> None:
    assert secret_lines(line) == ((1, "a credential assignment"),)


@pytest.mark.parametrize(
    "line",
    [
        "Fix the Safari crash in the toolbar",
        "Rotate the API token after the release",
        "See https://github.com/acme/shop/pull/12 and http://localhost:8080/x@y",
        "Clone with https://${USER}:${TOKEN}@github.com/acme/shop.git",
        "Task t-1fb17c23-90c1-42cf-93ac-94af0f21ddb6 blocks t-45aa06d8-773b-41ac-aedb-ce47efbe4ac6",
        "Commit 8c41d2e7a1b2c3d4e5f60718293a4b5c6d7e8f90 fixed it",
        "The secret is in the vault; ask for access to the api docs",
        "password: see the team vault",
    ],
)
def test_ordinary_lines_are_not_secrets(line: str) -> None:
    assert secret_lines(line) == ()


def test_the_projects_own_prose_holds_no_false_alarm() -> None:
    texts = [
        ROOT / "README.md",
        ROOT / "CHANGELOG.md",
        *ROOT.glob("spec/*"),
        *ROOT.glob("docs/*.md"),
    ]
    texts += sorted(ROOT.glob("todo/*/*.json"))
    assert [
        (path.name, secret_lines(path.read_text()))
        for path in texts
        if secret_lines(path.read_text())
    ] == []
