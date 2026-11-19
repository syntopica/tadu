from board_server import BoardServer


def token_of(board: BoardServer, cookie: str, now: float) -> str:
    """The GitHub token the board holds for the session this cookie names."""
    assert board.state.github is not None
    session = board.state.github.sessions.find(cookie.partition("=")[2], now)
    assert session is not None
    assert session.token is not None
    return session.token
