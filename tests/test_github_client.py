import pytest

from tadu.github_client import github_client


def test_reads_both_variables() -> None:
    environ = {"TADU_GITHUB_CLIENT_ID": " Iv1.abc ", "TADU_GITHUB_CLIENT_SECRET": "s3cret"}
    assert github_client(environ) == ("Iv1.abc", "s3cret")


@pytest.mark.parametrize(
    "environ",
    [
        {},
        {"TADU_GITHUB_CLIENT_ID": "Iv1.abc"},
        {"TADU_GITHUB_CLIENT_SECRET": "s3cret"},
        {"TADU_GITHUB_CLIENT_ID": " ", "TADU_GITHUB_CLIENT_SECRET": "s3cret"},
    ],
)
def test_missing_names_the_variables(environ: dict[str, str]) -> None:
    with pytest.raises(ValueError, match="TADU_GITHUB_CLIENT_ID and its secret in TADU_GITHUB"):
        github_client(environ)
