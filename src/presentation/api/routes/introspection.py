import logging
from typing import Any, Optional

from fastapi import APIRouter, Depends, Header, Request

from src.business_logic.services.introspection import IntrospectionServies
from src.data_access.postgresql.repositories import (
    ClientRepository,
    PersistentGrantRepository,
    UserRepository,
)
from src.presentation.api.models.introspection import (
    BodyRequestIntrospectionModel,
    ResponseIntrospectionModel,
)
from src.presentation.middleware.authorization_validation import (
    authorization_middleware,
)
from src.presentation.middleware.authorization_validation import (
    authorization_middleware,
)

logger = logging.getLogger(__name__)

introspection_router = APIRouter(
    prefix="/introspection",
    tags=["Introspection"],
    dependencies=[Depends(authorization_middleware)],
)


@introspection_router.post("/", response_model=ResponseIntrospectionModel)
async def post_introspection(
        request: Request,
        auth_swagger: Optional[str] = Header(
            default=None, description="Authorization"
        ),  # crutch for swagger
        request_body: BodyRequestIntrospectionModel = Depends(),
) -> dict[str, Any]:
    session = request.state.session
    introspection_class = IntrospectionServies(
        session=session,
        user_repo=UserRepository(session),
        persistent_grant_repo=PersistentGrantRepository(session),
        client_repo=ClientRepository(session),
    )
    introspection_class.request = request

    token = request.headers.get("authorization") or auth_swagger
    introspection_class.authorization = token
    introspection_class.request_body = request_body
    logger.debug(f"Introspection for token {request_body.token} started")
    return await introspection_class.analyze_token()
