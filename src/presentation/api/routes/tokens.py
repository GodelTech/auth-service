import logging
from typing import Any, Dict, Union, TypeAlias

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse

from src.business_logic.services import TokenService
from src.di.providers import provide_token_service_stub
from src.presentation.api.models.tokens import (
    BodyRequestTokenModel,
    ResponseTokenModel,
)


TokensResponse: TypeAlias = Union[JSONResponse, Dict[str, Any]]


logger = logging.getLogger(__name__)


token_router = APIRouter(prefix="/token", tags=["Token"])


@token_router.post("/", response_model=ResponseTokenModel)
async def get_tokens(
        request: Request,
        request_body: BodyRequestTokenModel = Depends(),
        token_class: TokenService = Depends(provide_token_service_stub),
) -> TokensResponse:
    token_class.request = request
    token_class.request_model = request_body
    result = await token_class.get_tokens()
    headers = {"Cache-Control": "no-store", "Pragma": "no-cache"}
    return JSONResponse(content=result, headers=headers)
