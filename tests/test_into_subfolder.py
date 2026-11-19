import pytest

from tadu.github_sign_in import GithubSignIn
from tadu.into_subfolder import into_subfolder


@pytest.mark.parametrize(
    ("path", "location"),
    [
        ("/tadu", "/tadu/"),
        ("/tadu?token=t", "/tadu/?token=t"),
        ("/tadu?", "/tadu/"),
    ],
)
def test_permanent_redirect_keeps_the_query(path: str, location: str) -> None:
    answer = into_subfolder(GithubSignIn("id", "secret", "https://example.com/tadu"), path)
    assert answer.response[:2] == (308, b"")
    assert answer.headers == (("Location", location),)
