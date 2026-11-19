from tadu.git_commit import GitCommit
from tadu.git_file_change import GitFileChange
from tadu.parse_git_log import parse_git_log

A, B, C, Z = "a" * 40, "b" * 40, "c" * 40, "0" * 40
S1, S2, S3 = "1" * 40, "2" * 40, "3" * 40
DATE = "2026-11-01T09:00:00+00:00"


def header(sha: str, parents: str, subject: str) -> str:
    return f"\x1e{sha}\x1f{parents}\x1f{DATE}\x1fAna\x1f{subject}\0"


def test_commits_with_files_and_a_merge() -> None:
    output = (
        header(S3, f"{S1} {S2}", "Merge")
        + f"\0::100644 100644 100644 {A} {B} {C} MM\0TODO.md\0"
        + header(S2, S1, "Close")
        + f"\n:100644 000000 {A} {Z} D\0TODO.md\0:000000 100644 {Z} {B} A\0TODO_LOG.md\0"
        + header(S1, "", "Start \x1f odd")
        + f"\n:000000 100644 {Z} {A} A\0TODO.md\0"
    )
    merge, close, start = parse_git_log(output)
    assert merge == GitCommit(
        S3, S3[:10], (S1, S2), DATE, "Ana", "Merge", (GitFileChange("TODO.md", (A, B), C),)
    )
    assert close.files == (
        GitFileChange("TODO.md", (A,), Z),
        GitFileChange("TODO_LOG.md", (Z,), B),
    )
    assert (start.parents, start.subject) == ((), "Start \x1f odd")


def test_nothing() -> None:
    assert parse_git_log("") == ()
