from fastapi import APIRouter, Cookie, Depends, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.config import SESSION_COOKIE_NAME
from app.models.database import get_db
from app.repositories import session_repository
from app.services import chat_service

router = APIRouter(dependencies=[Depends(get_current_user)])


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


@router.post("/chat/new")
def post_chat_new(db: Session = Depends(get_db)) -> RedirectResponse:
    """新しい会話セッションを開始する。既存の履歴はDBに残したまま、Cookieを新しいセッションIDに切り替える。"""
    new_session_id, _ = chat_service.start_session(db)
    response = RedirectResponse(url="/chat", status_code=303)
    response.set_cookie(SESSION_COOKIE_NAME, new_session_id, httponly=True, samesite="lax")
    return response


@router.post("/chat/switch/{session_id}")
def post_chat_switch(session_id: str, db: Session = Depends(get_db)) -> RedirectResponse:
    """既存の過去セッションにCookieを切り替え、その続きから会話できるようにする。"""
    if session_repository.get_session(db, session_id) is None:
        raise HTTPException(status_code=404, detail="指定した会話が見つかりません。")

    response = RedirectResponse(url="/chat", status_code=303)
    response.set_cookie(SESSION_COOKIE_NAME, session_id, httponly=True, samesite="lax")
    return response
