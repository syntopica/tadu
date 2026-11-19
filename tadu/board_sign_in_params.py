"""The parameters of the board that apply only with --auth github."""

from __future__ import annotations

from tadu.idle_timeout import idle_timeout
from tadu.non_negative_int import non_negative_int
from tadu.param import Param
from tadu.public_board_url import public_board_url
from tadu.sign_in_limit import sign_in_limit
from tadu.sign_in_settings import SIGN_IN_LIMIT

BOARD_SIGN_IN_PARAMS = (
    Param(
        "public_url",
        "text",
        "with --auth github, the address people open, such as https://tadu.example.com "
        "or https://example.com/tadu, whose /auth/callback is the app's callback URL "
        "(default: http://HOST:PORT)",
        parse=public_board_url,
    ),
    Param(
        "sign_in_limit",
        "text",
        "with --auth github, how often one address may start a sign-in, and come back "
        "from GitHub, each: like 10/minute or 10/minute;100/hour, or off "
        f"(default: {SIGN_IN_LIMIT})",
        metavar="LIMITS",
        parse=sign_in_limit,
    ),
    Param(
        "idle_timeout",
        "text",
        "with --auth github, sign a person out after this long without activity, "
        "such as 14d, 8h or 30m, at least 10m; an open page warns 5 minutes before "
        "(default: 14d)",
        metavar="DURATION",
        parse=idle_timeout,
    ),
    Param(
        "proxy_hops",
        "count",
        "with --auth github, how many proxies in front of the board to trust for the "
        "client's address in X-Forwarded-For (default: 0, the header is ignored)",
        metavar="N",
        parse=non_negative_int,
    ),
)
