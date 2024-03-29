import time
from typing import Any, Optional

from fastapi import APIRouter
from src.presentation.middleware.authorization_validation import OIDC_RESOURCE_NAME
from src.business_logic.services.jwt_token import JWTService

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
    jwt = JWTService()
    payload: dict[str, Any] = {"sub": "1"}
    if with_iss_me:
        payload["iss"] = "me"
    if with_aud:
        payload["aud"] = ["admin", f"{OIDC_RESOURCE_NAME}:introspection:read", f"{OIDC_RESOURCE_NAME}:revoke:post"] + scope.split(" ")
    if exp:
        payload["exp"] = exp
    return await jwt.encode_jwt(payload)


@debug_router.get("/decode_token", response_model=dict)
async def get_decode_token(
    token: str,
    issuer: Optional[str] = None,
    audience: Optional[str] = None,
) -> dict[str, Any]:
    jwt = JWTService()
    kwargs = {}
    if issuer is not None:
        kwargs["issuer"] = issuer
    if audience is not None:
        kwargs["audience"] = audience

    return await jwt.decode_token(token, **kwargs)

