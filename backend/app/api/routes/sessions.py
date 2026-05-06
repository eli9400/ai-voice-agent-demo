from fastapi import APIRouter, HTTPException

from app.schemas.sessions import (
    CreateSessionResponse,
    MessageRequest,
    MessageResponse,
    SessionDetailResponse,
)
from app.services.session_store import StoredSession, add_message, create_session, get_session

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


def _get_or_404(session_id: str) -> StoredSession:
    session = get_session(session_id)
    if session is None:
        raise HTTPException(
            status_code=404,
            detail=f"Session '{session_id}' not found",
        )
    return session


@router.post("", response_model=CreateSessionResponse, status_code=201)
def create_session_endpoint() -> CreateSessionResponse:
    session_id = create_session()
    return CreateSessionResponse(session_id=session_id, status="created")


@router.post("/{session_id}/messages", response_model=MessageResponse)
def add_session_message(
    session_id: str,
    payload: MessageRequest,
) -> MessageResponse:
    _get_or_404(session_id)
    message, message_count = add_message(session_id=session_id, content=payload.content)

    return MessageResponse(
        session_id=session_id,
        user_message=message["user_message"],
        assistant_message=message["assistant_message"],
        message_count=message_count,
    )


@router.get("/{session_id}", response_model=SessionDetailResponse)
def get_session_details(session_id: str) -> SessionDetailResponse:
    session = _get_or_404(session_id)
    return SessionDetailResponse(
        session_id=session["session_id"],
        messages=session["messages"],
    )
