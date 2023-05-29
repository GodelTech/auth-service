from __future__ import annotations
import logging
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from src.di.providers import provide_token_service_factory
from src.business_logic.get_tokens.dto import ResponseTokenModel, RequestTokenModel


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from src.business_logic.get_tokens.interfaces import TokenServiceProtocol
    from src.business_logic.get_tokens import TokenServiceFactory


logger = logging.getLogger(__name__)

token_router = APIRouter(prefix="/token", tags=["Token"])


@token_router.post("/")
async def get_tokens(
        request: Request,
        request_body: RequestTokenModel = Depends(RequestTokenModel.as_form)
) -> JSONResponse:
    session: AsyncSession = request.state.session
    logger.info("SESSION: ")
    logger.info(session)

    token_service_factory: TokenServiceFactory = provide_token_service_factory(db_session=session)
    token_service: TokenServiceProtocol = token_service_factory.get_service_impl(request_body.grant_type)
    result: ResponseTokenModel = await token_service.get_tokens(request_body)

    headers = {"Cache-Control": "no-store", "Pragma": "no-cache"}
    return JSONResponse(content=result.dict(exclude_none=True), headers=headers)
