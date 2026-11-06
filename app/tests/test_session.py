# Tests for the in-memory session store.

from app.session import SessionStore


def test_create_and_get():
    store = SessionStore()
    store.create("abc123", agent=object(), total_questions=5)
    session = store.get("abc123")
    assert session is not None
    assert session["total_questions"] == 5
    assert session["current_idx"] == 0
    assert session["scores"] == []


def test_get_missing_returns_none():
    assert SessionStore().get("nope") is None


def test_update_idx():
    store = SessionStore()
    store.create("s1", agent=object(), total_questions=3)
    store.update_idx("s1", 2)
    assert store.get("s1")["current_idx"] == 2


def test_update_idx_unknown_session_is_noop():
    SessionStore().update_idx("ghost", 1)  # must not raise


def test_delete():
    store = SessionStore()
    store.create("s1", agent=object(), total_questions=3)
    store.delete("s1")
    assert store.get("s1") is None
    store.delete("s1")  # deleting twice must not raise


def test_len_and_list():
    store = SessionStore()
    store.create("a", agent=object(), total_questions=1)
    store.create("b", agent=object(), total_questions=1)
    assert len(store) == 2
    assert sorted(store.list_sessions()) == ["a", "b"]
