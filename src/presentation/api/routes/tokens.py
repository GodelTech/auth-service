import logging
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from src.di.providers import provide_token_service_factory_stub
from src.business_logic.get_tokens.dto import ResponseTokenModel, RequestTokenModel
from src.business_logic.get_tokens import TokenServiceFactory

from typing import Union, Any, TYPE_CHECKING
if TYPE_CHECKING:
    from src.business_logic.get_tokens.interfaces import TokenServiceProtocol


TokenEndpointResponse = Union[JSONResponse, dict[str, Any]]


logger = logging.getLogger(__name__)


token_router = APIRouter(prefix="/token", tags=["Token"])


@token_router.post("/")
async def get_tokens(
        request_body: RequestTokenModel = Depends(),
        token_service_factory: TokenServiceFactory = Depends(provide_token_service_factory_stub),
) -> TokenEndpointResponse:
    token_service: 'TokenServiceProtocol' = token_service_factory.get_service_impl(request_body.grant_type)
    result: ResponseTokenModel = await token_service.get_tokens(request_body)
    headers = {"Cache-Control": "no-store", "Pragma": "no-cache"}
    return JSONResponse(content=result.dict(exclude_none=True), headers=headers)
