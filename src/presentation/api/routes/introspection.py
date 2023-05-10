import logging
from typing import Any, Optional, Union

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from jwt.exceptions import ExpiredSignatureError

from src.business_logic.services.introspection import IntrospectionServies
from src.di.providers import provide_introspection_service_stub
from src.presentation.api.models.introspection import (
    BodyRequestIntrospectionModel,
    ResponceIntrospectionModel,
)

logger = logging.getLogger(__name__)

introspection_router = APIRouter(
    prefix="/introspection", tags=["Introspection"]
)


@introspection_router.post("/", response_model=ResponceIntrospectionModel)
async def post_introspection(
    request: Request,
    auth_swagger: Optional[str] = Header(
        default=None, description="Authorization"
    ),  # crutch for swagger
    request_body: BodyRequestIntrospectionModel = Depends(),
) -> dict[str, Any]:
    try:
        session = request.state.session
        introspection_class = IntrospectionServies(session)
        introspection_class.request = request

        token = request.headers.get("authorization") or auth_swagger
        introspection_class.authorization = token
        introspection_class.request_body = request_body
        logger.debug(f"Introspection for token {request_body.token} started")
        return await introspection_class.analyze_token()

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect Token"
        )
