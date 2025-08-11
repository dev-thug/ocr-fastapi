from __future__ import annotations
from fastapi import Header, HTTPException
from app.core.config import settings
from jose import jwk, jwt
from jose.utils import base64url_decode
import time
import requests


_jwks_cache: dict[str, dict] = {}


def _get_cognito_jwks(issuer: str) -> dict:
    if issuer in _jwks_cache and (time.time() - _jwks_cache[issuer]["_ts"]) < 3600:
        return _jwks_cache[issuer]["keys"]
    url = issuer.rstrip("/") + "/.well-known/jwks.json"
    resp = requests.get(url, timeout=5)
    resp.raise_for_status()
    keys = resp.json()
    _jwks_cache[issuer] = {"keys": keys, "_ts": time.time()}
    return keys


def _verify_jwt(token: str, issuer: str, audience: str | None = None) -> None:
    headers = jwt.get_unverified_header(token)
    kid = headers.get("kid")
    keys = _get_cognito_jwks(issuer)
    key = next((k for k in keys["keys"] if k["kid"] == kid), None)
    if not key:
        raise HTTPException(status_code=401, detail="Invalid token (kid)")
    message, encoded_sig = token.rsplit(".", 1)
    decoded_sig = base64url_decode(encoded_sig.encode("utf-8"))
    public_key = jwk.construct(key)
    if not public_key.verify(message.encode("utf-8"), decoded_sig):
        raise HTTPException(status_code=401, detail="Invalid signature")
    claims = jwt.get_unverified_claims(token)
    if issuer and claims.get("iss") != issuer.rstrip("/"):
        raise HTTPException(status_code=401, detail="Invalid issuer")
    if audience and audience not in claims.get("aud", ""):
        raise HTTPException(status_code=401, detail="Invalid audience")
    if time.time() > claims.get("exp", 0):
        raise HTTPException(status_code=401, detail="Token expired")


async def require_auth(authorization: str | None = Header(default=None), x_api_key: str | None = Header(default=None, alias="x-api-key")) -> None:
    mode = (settings.auth_mode or "api-key").lower()
    if mode == "api-key":
        if settings.api_key:
            if not x_api_key or x_api_key != settings.api_key:
                raise HTTPException(status_code=401, detail="Invalid API key")
        return
    elif mode == "cognito":
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing Authorization header")
        token = authorization.split(" ", 1)[1]
        issuer = (settings.cognito_issuer or "").strip()
        audience = (settings.cognito_audience or None)
        if not issuer:
            raise HTTPException(status_code=500, detail="Cognito issuer not configured")
        _verify_jwt(token, issuer, audience)
        return
    else:
        raise HTTPException(status_code=500, detail="Unsupported AUTH_MODE")
