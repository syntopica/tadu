import re
from pathlib import Path

import pytest

CSS = (Path(__file__).parent.parent / "tadu" / "board" / "board.css").read_text()
TOKEN = re.compile(r"^\s*--([\w-]+): (?:light-dark\((#\w{6}), (#\w{6})\)|(#\w{6}));", re.MULTILINE)
# Each token as (light, dark): the :root block gives both through light-dark().
TOKENS = {match[1]: (match[2] or match[4], match[3] or match[4]) for match in TOKEN.finditer(CSS)}
SURFACES = ("bg", "sidebar", "surface", "surface-2", "raised", "group-row")
TEXT = [(text, surface) for text in ("text", "muted", "faint") for surface in SURFACES]
BADGES = [(f"{name}-ink", f"{name}-bg") for name in ("urgent", "high", "normal", "low")]
ACCENTS = [("accent-text", "accent"), ("accent-ink", "accent-soft"), ("blocked-ink", "surface")]


def luminance(colour: str) -> float:
    channels = [int(colour[index : index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def ratio(first: str, second: str) -> float:
    light, dark = sorted((luminance(first), luminance(second)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


@pytest.mark.parametrize(("text", "background"), [*TEXT, *BADGES, *ACCENTS])
def test_text_meets_wcag_aa_in_both_schemes(text: str, background: str) -> None:
    for scheme in (0, 1):
        contrast = ratio(TOKENS[text][scheme], TOKENS[background][scheme])
        assert contrast >= 4.5, (text, background, ["light", "dark"][scheme], contrast)


def test_every_colour_token_was_read() -> None:
    assert len(TOKENS) >= 30
    assert TOKENS["faint"] == ("#666d80", "#858ca3")
