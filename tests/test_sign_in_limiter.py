import pytest
from board_clock import BoardClock

from tadu.sign_in_limit import sign_in_limit
from tadu.sign_in_limiter import SignInLimiter
from tadu.sign_in_settings import SIGN_IN_LIMIT


@pytest.fixture
def clock(monkeypatch: pytest.MonkeyPatch) -> BoardClock:
    return BoardClock(monkeypatch)


def allowed(
    limiter: SignInLimiter, times: int, path: str = "/auth/login", address: str = "a"
) -> int:
    return sum(limiter.hit(path, address) is None for _ in range(times))


def test_the_default_is_ten_a_minute_per_address(clock: BoardClock) -> None:
    limiter = SignInLimiter()
    assert SIGN_IN_LIMIT == "10/minute"
    assert allowed(limiter, 10) == 10
    assert limiter.hit("/auth/login", "a") == 60
    clock.advance(30)
    assert limiter.hit("/auth/login", "a") == 30
    clock.advance(30.5)
    assert allowed(limiter, 10) == 10


def test_the_window_moves_with_time(clock: BoardClock) -> None:
    limiter = SignInLimiter()
    for _ in range(10):
        assert limiter.hit("/auth/login", "a") is None
        clock.advance(6)
    clock.advance(0.5)
    assert limiter.hit("/auth/login", "a") is None
    assert limiter.hit("/auth/login", "a") is not None


def test_at_the_very_edge_of_a_window_nothing_slips_through_uncounted(clock: BoardClock) -> None:
    limiter = SignInLimiter()
    for _ in range(10):
        limiter.hit("/auth/login", "a")
        clock.advance(6)
    let_in = sum(limiter.hit("/auth/login", "a") is None for _ in range(20))
    assert let_in <= 1


def test_paths_and_addresses_each_have_their_own(clock: BoardClock) -> None:
    limiter = SignInLimiter()
    assert allowed(limiter, 10) == 10
    assert allowed(limiter, 10, path="/auth/callback") == 10
    assert allowed(limiter, 10, address="b") == 10
    assert allowed(limiter, 1) == 0
    assert clock.now


def test_every_limit_given_holds(clock: BoardClock) -> None:
    limiter = SignInLimiter(sign_in_limit("3/minute;5/hour"))
    assert allowed(limiter, 4) == 3
    clock.advance(60.5)
    assert allowed(limiter, 3) == 2
    assert limiter.hit("/auth/login", "a") == 3600 - 60
    clock.advance(3600)
    assert allowed(limiter, 3) == 3


def test_refused_requests_are_not_counted(clock: BoardClock) -> None:
    limiter = SignInLimiter(sign_in_limit("2/minute"))
    assert allowed(limiter, 50) == 2
    clock.advance(60.5)
    assert allowed(limiter, 2) == 2


def test_off_limits_nothing(clock: BoardClock) -> None:
    limiter = SignInLimiter(sign_in_limit("off"))
    assert allowed(limiter, 500) == 500
    assert clock.now
