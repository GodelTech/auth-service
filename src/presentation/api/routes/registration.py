import logging
from fastapi import APIRouter, Depends, Header, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.presentation.api.models.registration import (
    ClientRequestModel,
    ClientUpdateRequestModel,
    ClientResponseModel,
)
from src.business_logic.services.client import ClientService
from src.data_access.postgresql.errors import ClientNotFoundError
from typing import Any
from src.data_access.postgresql.repositories import ClientRepository

from src.presentation.middleware.access_token_validation import (
    access_token_middleware,
)
from src.di.providers import provide_async_session_stub

logger = logging.getLogger(__name__)

client_router = APIRouter(prefix="/clients", tags=["Client"])


@client_router.post("/register", response_model=ClientResponseModel)
async def register_client(
    request: Request,
    request_body: ClientRequestModel = Depends(),
    session: AsyncSession = Depends(provide_async_session_stub),
) -> dict[str, str]:
    client_service = ClientService(
        session=session, client_repo=ClientRepository(session)
    )
    client_service.request_model = request_body
    response = await client_service.registration()
    await session.commit()
    return response


@client_router.put("/{client_id}", response_model=dict)
async def update_client(
    client_id: str,
    request: Request,
    request_body: ClientUpdateRequestModel = Depends(),
    session: AsyncSession = Depends(provide_async_session_stub),
) -> dict[str, str]:
    client_service = ClientService(
        session=session, client_repo=ClientRepository(session)
    )
    client_service.request_model = request_body
    await client_service.update(client_id=client_id)
    await session.commit()
    return {"message": "Client data updated successfully"}


@client_router.get("", response_model=dict)
async def get_all_clients(
    request: Request,
    access_token: str = Header(description="Access token"),
    auth: None = Depends(access_token_middleware),
    session: AsyncSession = Depends(provide_async_session_stub),
    client_service = ClientService(
        session=session, client_repo=ClientRepository(session)
    )
    return {"all_clients": await client_service.get_all()}


@client_router.get("/{client_id}", response_model=dict)
async def get_client(
    client_id: str,
    request: Request,
    session: AsyncSession = Depends(provide_async_session_stub),
) -> dict[str, Any]:
    client_service = ClientService(
        session=session, client_repo=ClientRepository(session)
    )
    return await client_service.get_client_by_client_id(client_id=client_id)


@client_router.delete("/{client_id}", status_code=status.HTTP_200_OK)
async def delete_client(
    client_id: str,
    request: Request,
    session: AsyncSession = Depends(provide_async_session_stub),
) -> dict[str, Any]:
    client_service = ClientService(
        session=session, client_repo=ClientRepository(session)
    )
    if not await client_service.client_repo.validate_client_by_client_id(
        client_id=client_id
    ):
        raise ClientNotFoundError
    await client_service.client_repo.delete_client_by_client_id(
        client_id=client_id
    )
    await session.commit()
    return {"message": "Client deleted successfully"}
