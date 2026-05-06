from typing import TypedDict
from uuid import uuid4


class StoredMessage(TypedDict):
    user_message: str
    assistant_message: str


class StoredSession(TypedDict):
    session_id: str
    messages: list[StoredMessage]


_sessions: dict[str, StoredSession] = {}


def create_session() -> str:
    session_id = str(uuid4())
    _sessions[session_id] = {
        "session_id": session_id,
        "messages": [],
    }
    return session_id


def get_session(session_id: str) -> StoredSession | None:
    return _sessions.get(session_id)


def add_message(session_id: str, content: str) -> tuple[StoredMessage, int]:
    session = _sessions.get(session_id)
    if session is None:
        raise KeyError(f"Session '{session_id}' not found")

    assistant_message = f"Mock AI response: {content}"
    message: StoredMessage = {
        "user_message": content,
        "assistant_message": assistant_message,
    }
    session["messages"].append(message)
    return message, len(session["messages"])
