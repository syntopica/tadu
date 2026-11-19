"""How many pages a paginated GitHub answer has."""

from __future__ import annotations

from urllib.parse import parse_qs, urlsplit


def last_page(links: dict[str, dict[str, str]]) -> int:
    """The `page` of the Link header's `rel="last"` URL; 1 when there is none."""
    url = links.get("last", {}).get("url", "")
    pages = parse_qs(urlsplit(url).query).get("page", [])
    return int(pages[0]) if pages and pages[0].isdigit() else 1
