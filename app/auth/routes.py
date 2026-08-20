import secrets

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from app.auth.cognito import build_login_url, build_logout_url, exchange_code_for_tokens, verify_id_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login")
def login(request: Request, next: str = "/chat") -> RedirectResponse:
    state = secrets.token_urlsafe(16)
    request.session["oauth_state"] = state
    request.session["next"] = next if next.startswith("/") else "/chat"
    return RedirectResponse(build_login_url(state))


@router.get("/callback")
def callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
) -> RedirectResponse:
    expected_state = request.session.pop("oauth_state", None)
    if error or not code or not state or state != expected_state:
        return RedirectResponse("/auth/login")

    tokens = exchange_code_for_tokens(code)
    claims = verify_id_token(tokens["id_token"])

    request.session["user"] = {"sub": claims["sub"], "email": claims.get("email", "")}
    next_path = request.session.pop("next", "/chat")
    return RedirectResponse(next_path)


@router.get("/logout")
def logout(request: Request) -> RedirectResponse:
    request.session.clear()
    return RedirectResponse(build_logout_url())
