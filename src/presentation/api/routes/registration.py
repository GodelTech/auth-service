import logging
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from src.presentation.api.models.registration import ClientRequestModel, ClientUpdateRequestModel, ClientResponseModel  
from src.business_logic.services import ClientService, ScopeService
from src.di.providers.services import provide_client_service_stub
from src.data_access.postgresql.errors import ClientNotFoundError
from typing import Any, Callable
from pydantic import ValidationError
from src.data_access.postgresql.repositories import ClientRepository, ResourcesRepository
from functools import wraps
from src.presentation.middleware.access_token_validation import access_token_middleware

logger = logging.getLogger(__name__)

client_router = APIRouter(
    prefix="/clients", tags=["Client"]
)

@client_router.post("/register", response_model = ClientResponseModel)
async def register_client(
    request: Request,
    request_body: ClientRequestModel = Depends(),
    ) -> dict[str, str]:
    session = request.state.session
    client_service = ClientService(
        session=session, 
        client_repo=ClientRepository(session),
        scope_service=ScopeService(
            resource_repo=ResourcesRepository(session),
            session=session, 
            )
    )
    client_service.request_model = request_body
    response = await client_service.registration() 
    return response


@client_router.put("/{client_id}", response_model=dict)
async def update_client(
    client_id: str, 
    request: Request,
    request_body: ClientUpdateRequestModel = Depends(),
    ) -> dict[str, str]:
    session = request.state.session
    client_service = ClientService(
        session=session, 
        client_repo=ClientRepository(session),
        scope_service=ScopeService(
            resource_repo=ResourcesRepository(session),
            session=session, 
            )
    )
    client_service.request_model = request_body
    await client_service.update(client_id=client_id)
    return {"message": "Client data updated successfully"}


@client_router.get("", response_model=dict)
async def get_all_clients(
    request: Request,
    access_token: str = Header(description="Access token"),
    client_service: ClientService = Depends(provide_client_service_stub),
    auth:None = Depends(access_token_middleware)
    )->dict[str,list[dict[str, Any]]]:
    session = request.state.session
    client_service = ClientService(
        session=session, 
        client_repo=ClientRepository(session),
        scope_service=ScopeService(
            resource_repo=ResourcesRepository(session),
            session=session, 
            )
    )
    return{"all_clients": await client_service.get_all()}

@client_router.get("/{client_id}", response_model=dict)
async def get_client(
    client_id:str,
    request: Request,
    client_service: ClientService = Depends(provide_client_service_stub),
    )->dict[str, Any]:
    session = request.state.session
    client_service = ClientService(
        session=session, 
        client_repo=ClientRepository(session),
        scope_service=ScopeService(
            resource_repo=ResourcesRepository(session),
            session=session, 
            )
    )
    return await client_service.get_client_by_client_id(client_id=client_id)


@client_router.delete("/{client_id}", status_code=status.HTTP_200_OK)
async def delete_client(
    client_id:str,
    request: Request,
    client_service: ClientService = Depends(provide_client_service_stub),
    )->dict[str, Any]:
    session = request.state.session
    client_service = ClientService(
        session=session, 
        client_repo=ClientRepository(session),
        scope_service=ScopeService(
            resource_repo=ResourcesRepository(session),
            session=session, 
            )
    )
    if not await client_service.client_repo.validate_client_by_client_id(client_id=client_id):
        raise ClientNotFoundError
    await client_service.client_repo.delete_client_by_client_id(client_id=client_id)
    return {"message": "Client deleted successfully"}
