from tadu.line_commit_times import line_commit_times

SHA = "b" * 40
OUTPUT = f"""{SHA} 1 1 2
author x
committer-time 100
summary {SHA} 9 9
\t- [!] a
{SHA} 2 2
committer-time 100
\tcommitter-time 7
{"0" * 40} 3 3 1
committer-time 300
\t- [ ] b
"""


def test_maps_final_lines_to_times() -> None:
    assert line_commit_times(OUTPUT) == {1: 100, 2: 100, 3: 300}


def test_empty() -> None:
    assert line_commit_times("") == {}
