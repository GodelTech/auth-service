import time
from typing import Any, Optional

from fastapi import APIRouter

from src.di.providers import provide_jwt_manager

debug_router = APIRouter(
    prefix="/userinfo",
    tags=["Debug Swagger"],
)


@debug_router.get("/get_default_token", response_model=str)
async def get_default_token(
    with_iss_me: Optional[bool] = None,
    with_aud: Optional[bool] = True,
    exp: Optional[int] = int(time.time() + 10000),
    scope: str = "profile",
) -> str:
    jwt = provide_jwt_manager()
    payload: dict[str, Any] = {"sub": "1", "scope": scope}
    if with_iss_me:
        payload["iss"] = "me"
    if with_aud:
        payload["aud"] = ["admin", "userinfo", "introspection", "revoke"]
    if exp:
        payload["exp"] = exp
    return await jwt.encode(payload)


@debug_router.get("/decode_token", response_model=dict)
async def get_decode_token(
    token: str,
    issuer: Optional[str] = None,
    audience: Optional[str] = None,
) -> dict[str, Any]:
    jwt = provide_jwt_manager()
    kwargs = {}
    if issuer is not None:
        kwargs["issuer"] = issuer
    if audience is not None:
        kwargs["audience"] = audience

    return await jwt.decode_token(token, **kwargs)

