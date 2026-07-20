from fastapi import APIRouter, Cookie, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import SESSION_COOKIE_NAME
from app.models.database import get_db
from app.repositories import session_repository
from app.services import review_service

router = APIRouter()


class ReviewRequest(BaseModel):
    proposal: str


class ReviewResponse(BaseModel):
    result: str


@router.post("/review", response_model=ReviewResponse)
def post_review(
    body: ReviewRequest,
    db: Session = Depends(get_db),
    session_id: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
) -> ReviewResponse:
    if not session_id or session_repository.get_session(db, session_id) is None:
        raise HTTPException(
            status_code=400,
            detail="セッションが存在しません。先にチャット画面を開いてください。",
        )
    if not body.proposal.strip():
        raise HTTPException(status_code=400, detail="proposal must not be empty")

    result = review_service.review_proposal(db, session_id, body.proposal)
    return ReviewResponse(result=result)
