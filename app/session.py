# app/session.py
# In-memory session store for interview sessions

from typing import Optional


class SessionStore:
    """Thread-safe in-memory store for active interview sessions."""

    def __init__(self):
        self._store: dict = {}

    def create(self, session_id: str, agent, total_questions: int) -> dict:
        session = {
            "agent": agent,
            "total_questions": total_questions,
            "current_idx": 0,
            "scores": [],
        }
        self._store[session_id] = session
        return session

    def get(self, session_id: str) -> Optional[dict]:
        return self._store.get(session_id)

    def update_idx(self, session_id: str, idx: int):
        if session_id in self._store:
            self._store[session_id]["current_idx"] = idx

    def delete(self, session_id: str):
        self._store.pop(session_id, None)

    def list_sessions(self) -> list:
        return list(self._store.keys())

    def __len__(self) -> int:
        return len(self._store)
