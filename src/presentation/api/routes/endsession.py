import logging
from typing import Union

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.business_logic.services.endsession import EndSessionService
from src.data_access.postgresql.repositories import (
    ClientRepository,
    PersistentGrantRepository,
)
from src.presentation.api.models.endsession import RequestEndSessionModel
from src.di.providers import provide_async_session_stub

logger = logging.getLogger(__name__)

endsession_router = APIRouter(prefix="/endsession", tags=["End Session"])


@endsession_router.get(
    "/", status_code=status.HTTP_204_NO_CONTENT, response_model=None
)
async def end_session(
    request: Request,
    request_model: RequestEndSessionModel = Depends(),
    session: AsyncSession = Depends(provide_async_session_stub)
) -> Union[int, RedirectResponse, JSONResponse]:
    session = session
    service_class = EndSessionService(
        session=session,
        client_repo=ClientRepository(session),
        persistent_grant_repo=PersistentGrantRepository(session),
    )
    service_class.request_model = request_model
    logout_redirect_uri = await service_class.end_session()
    if logout_redirect_uri is None:
        return status.HTTP_204_NO_CONTENT

    response = RedirectResponse(
        logout_redirect_uri, status_code=status.HTTP_302_FOUND
    )
    return response
