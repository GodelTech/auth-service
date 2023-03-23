import logging
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from src.presentation.api.models.registration import ClientRequestModel, ClientUpdateRequestModel, ClientResponseModel  
from src.business_logic.services.client import ClientService
from src.di.providers.services import provide_client_service_stub
from typing import Any
logger = logging.getLogger(__name__)

client_router = APIRouter(
    prefix="/clients", tags=["Client"]
)
@client_router.post("/register", response_model = ClientResponseModel)
async def register_client(
    request_body: ClientRequestModel = Depends(),
    client_service: ClientService = Depends(provide_client_service_stub)
    ) -> dict[str, str]:
    client_service.request_model = request_body
    response = await client_service.registration() 
    return response

@client_router.put("/{client_id}", response_model=dict)
async def update_client(
    client_id: str, 
    request_body: ClientUpdateRequestModel = Depends(),
    client_service: ClientService = Depends(provide_client_service_stub)
    ) -> dict[str, str]:
    client_service.request_model = request_body
    await client_service.update(client_id=client_id)
    return {"message": "Client data updated successfully"}

@client_router.get("", response_model=dict)
async def get_all_clients(
        access_token: str = Header(description="Access token"),
    client_service: ClientService = Depends(provide_client_service_stub)
    )->dict[str,list[dict[str, Any]]]:
    return{"all_clients": await client_service.get_all()}

@client_router.get("/{client_id}", response_model=dict)
async def get_client(
    client_id:str,
    client_service: ClientService = Depends(provide_client_service_stub)
    )->dict[str, Any]:

    return await client_service.get_client_by_client_id(client_id=client_id)
