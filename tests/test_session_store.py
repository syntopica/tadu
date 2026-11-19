from tadu.session_id import session_id
from tadu.session_store import SessionStore
from tadu.sign_in_settings import IDLE_TIMEOUT_SECONDS, SESSIONS_PER_LOGIN
from tadu.token_grant import TokenGrant

GRANT = TokenGrant("tok-ana", 500, "ref-ana")


def test_create_find_save_and_drop() -> None:
    store = SessionStore()
    cookie = store.create("ana", GRANT, 100.0)
    assert len(cookie) >= 43
    session = store.find(cookie, 101.0)
    assert session is not None
    assert session.id == session_id(cookie)
    assert (session.login, session.expires) == ("ana", 100 + IDLE_TIMEOUT_SECONDS)
    assert (session.token, session.token_expires, session.refresh_token) == (
        "tok-ana",
        500,
        "ref-ana",
    )
    renewed = session.__class__(
        session.id, "ana", 100 + IDLE_TIMEOUT_SECONDS, "tok-2", 900, "ref-2"
    )
    store.save(cookie, renewed)
    assert store.find(cookie, 101.0) == renewed
    assert store.find("other", 101.0) is None
    assert store.find(None, 101.0) is None
    assert store.find("", 101.0) is None
    store.drop(cookie)
    store.drop(cookie)
    store.drop(None)
    assert store.find(cookie, 101.0) is None
    store.save(cookie, renewed)
    assert store.find(cookie, 101.0) is None


def test_sessions_end_and_are_pruned() -> None:
    store = SessionStore()
    old = store.create("ana", GRANT, 0.0)
    assert store.find(old, IDLE_TIMEOUT_SECONDS - 1) is not None
    assert store.find(old, IDLE_TIMEOUT_SECONDS) is None
    new = store.create("bo", GRANT, IDLE_TIMEOUT_SECONDS + 1)
    assert len(store._sessions) == 1  # noqa: SLF001
    assert store.find(new, IDLE_TIMEOUT_SECONDS + 2) is not None


def test_the_store_never_holds_the_cookie_or_a_token() -> None:
    store = SessionStore()
    cookie = store.create("ana", GRANT, 0.0)
    assert cookie not in store._sessions  # noqa: SLF001
    assert "tok-ana" not in repr(store._sessions)  # noqa: SLF001
    assert "ref-ana" not in repr(store._sessions)  # noqa: SLF001


def test_one_login_holds_at_most_its_share_of_sessions() -> None:
    store = SessionStore()
    bo = store.create("bo", GRANT, 0.0)
    cookies = [store.create("Ana" if n % 2 else "ana", GRANT, float(n)) for n in range(25)]
    kept = [cookie for cookie in cookies if store.find(cookie, 30.0) is not None]
    assert kept == cookies[-SESSIONS_PER_LOGIN:]
    assert store.find(bo, 30.0) is not None


def test_each_session_has_one_lock_for_renewing() -> None:
    store = SessionStore()
    ana, bo = store.create("ana", GRANT, 0.0), store.create("bo", GRANT, 0.0)
    assert store.lock(ana) is store.lock(ana)
    assert store.lock(ana) is not store.lock(bo)
    store.drop(ana)
    assert store.lock(ana) is not None
