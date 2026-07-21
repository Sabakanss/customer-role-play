from contextlib import asynccontextmanager

from fastapi import Cookie, Depends, FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.api import chat, review
from app.config import SESSION_COOKIE_NAME
from app.models.database import get_db, init_db
from app.repositories import review_repository, session_repository
from app.services import chat_service
from app.utils.scenario_loader import load_scenario


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="AI顧客ヒアリング演習アプリ", lifespan=lifespan)
templates = Jinja2Templates(directory="app/templates")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(chat.router)
app.include_router(review.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse(url="/chat")


@app.get("/chat", response_class=HTMLResponse)
def chat_page(
    request: Request,
    db: Session = Depends(get_db),
    session_id: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
) -> HTMLResponse:
    if not session_id or session_repository.get_session(db, session_id) is None:
        session_id, _ = chat_service.start_session(db)

    history = chat_service.get_history(db, session_id)
    customer_role = load_scenario().customer_role
    response = templates.TemplateResponse(
        request, "chat.html", {"history": history, "customer_role": customer_role}
    )
    response.set_cookie(SESSION_COOKIE_NAME, session_id, httponly=True, samesite="lax")
    return response


@app.get("/sessions", response_class=HTMLResponse)
def sessions_page(
    request: Request,
    db: Session = Depends(get_db),
    session_id: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
) -> HTMLResponse:
    sessions = chat_service.list_sessions_summary(db)
    return templates.TemplateResponse(
        request, "sessions.html", {"sessions": sessions, "current_session_id": session_id}
    )


@app.get("/review", response_class=HTMLResponse, response_model=None)
def review_page(
    request: Request,
    db: Session = Depends(get_db),
    session_id: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
):
    if not session_id or session_repository.get_session(db, session_id) is None:
        return RedirectResponse(url="/chat")

    reviews = review_repository.get_reviews(db, session_id)
    customer_role = load_scenario().customer_role
    return templates.TemplateResponse(
        request, "review.html", {"reviews": reviews, "customer_role": customer_role}
    )
