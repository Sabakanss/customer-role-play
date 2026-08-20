"""Amazon Cognito Hosted UI を使ったOIDC認証（Authorization Code Grant）のヘルパー。"""

from urllib.parse import urlencode

import httpx
import jwt
from jwt import PyJWKClient

from app.config import settings

_ISSUER = f"https://cognito-idp.{settings.cognito_region}.amazonaws.com/{settings.cognito_user_pool_id}"
_JWKS_URL = f"{_ISSUER}/.well-known/jwks.json"
_jwk_client = PyJWKClient(_JWKS_URL)


def _redirect_uri() -> str:
    return f"{settings.app_base_url}/auth/callback"


def build_login_url(state: str) -> str:
    params = {
        "client_id": settings.cognito_client_id,
        "response_type": "code",
        "scope": "openid email",
        "redirect_uri": _redirect_uri(),
        "state": state,
    }
    return f"{settings.cognito_domain}/oauth2/authorize?{urlencode(params)}"


def build_logout_url() -> str:
    params = {
        "client_id": settings.cognito_client_id,
        "logout_uri": f"{settings.app_base_url}/",
    }
    return f"{settings.cognito_domain}/logout?{urlencode(params)}"


def exchange_code_for_tokens(code: str) -> dict:
    data = {
        "grant_type": "authorization_code",
        "client_id": settings.cognito_client_id,
        "code": code,
        "redirect_uri": _redirect_uri(),
    }
    auth = None
    if settings.cognito_client_secret:
        auth = (settings.cognito_client_id, settings.cognito_client_secret)
    response = httpx.post(
        f"{settings.cognito_domain}/oauth2/token",
        data=data,
        auth=auth,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10.0,
    )
    response.raise_for_status()
    return response.json()


def verify_id_token(id_token: str) -> dict:
    """IDトークンの署名・発行者・宛先・有効期限を検証し、claimsを返す。"""
    signing_key = _jwk_client.get_signing_key_from_jwt(id_token)
    return jwt.decode(
        id_token,
        signing_key.key,
        algorithms=["RS256"],
        audience=settings.cognito_client_id,
        issuer=_ISSUER,
    )
