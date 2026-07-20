from fastapi import APIRouter, Cookie, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import SESSION_COOKIE_NAME
from app.models.database import get_db
from app.repositories import session_repository
from app.services import chat_service

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatResponse)
def post_chat(
    body: ChatRequest,
    db: Session = Depends(get_db),
    session_id: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
) -> ChatResponse:
    if not session_id or session_repository.get_session(db, session_id) is None:
        raise HTTPException(
            status_code=400,
            detail="セッションが存在しません。先にチャット画面を開いてください。",
        )
    if not body.message.strip():
        raise HTTPException(status_code=400, detail="message must not be empty")

    reply = chat_service.send_message(db, session_id, body.message)
    return ChatResponse(reply=reply)
