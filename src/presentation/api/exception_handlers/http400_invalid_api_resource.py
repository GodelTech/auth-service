from src.data_access.postgresql.errors import ResourceNotFoundError
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST


async def http400_invalid_api_resource(
    _: Request, exc: ResourceNotFoundError
) -> JSONResponse:
    headers = {"Cache-Control": "no-store", "Pragma": "no-cache"}
    content = {"error": "invalid api resource in your scope"}
    return JSONResponse(
        content=content, headers=headers, status_code=HTTP_400_BAD_REQUEST
    )
