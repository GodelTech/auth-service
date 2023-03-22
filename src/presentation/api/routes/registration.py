import logging
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from src.presentation.api.models.registration import ClientRequestModel, ClientUpdateRequestModel, ClientResponseModel  
from src.business_logic.services.client import ClientService
from src.di.providers.services import provide_client_service_stub

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
    responce = await client_service.registration() 
    return responce

@client_router.put("/{client_id}", response_model=dict)
async def update_client(
    client_id: str, 
    request_body: ClientUpdateRequestModel = Depends(),
    client_service: ClientService = Depends(provide_client_service_stub)
    ) -> dict[str, str]:
    client_service.request_model = request_body
    await client_service.update(client_id=client_id)
    return {"message": "Client data updated successfully"}