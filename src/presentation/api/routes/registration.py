import logging
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from src.presentation.api.models.registration import ClientRequestModel, ClientUpdateRequestModel, ClientResponseModel  
from src.business_logic.services.client import ClientService
from src.di.providers.services import provide_client_service_stub
from src.data_access.postgresql.errors import ClientNotFoundError
from typing import Any, Callable
from pydantic import ValidationError
from src.data_access.postgresql.repositories import ClientRepository
from functools import wraps

logger = logging.getLogger(__name__)

client_router = APIRouter(
    prefix="/clients", tags=["Client"]
)

def exceptions_wrapper(func:Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    async def inner(*args:Any, **kwargs:Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except ClientNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Client not found"
            )
        except ValidationError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="BAD_REQUEST"
            )
        except:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="INTERNAL_SERVER_ERROR",
            )
    return inner


@client_router.post("/register", response_model = ClientResponseModel)
@exceptions_wrapper
async def register_client(
    request: Request,
    request_body: ClientRequestModel = Depends(),
    ) -> dict[str, str]:
    session = request.state.session
    client_service = ClientService(
        session=session, 
        client_repo=ClientRepository(session)
    )
    client_service.request_model = request_body
    response = await client_service.registration() 
    return response


@client_router.put("/{client_id}", response_model=dict)
@exceptions_wrapper
async def update_client(
    client_id: str, 
    request: Request,
    request_body: ClientUpdateRequestModel = Depends(),
    client_service: ClientService = Depends(provide_client_service_stub)
    ) -> dict[str, str]:
    session = request.state.session
    client_service = ClientService(
        session=session, 
        client_repo=ClientRepository(session)
    )
    client_service.request_model = request_body
    await client_service.update(client_id=client_id)
    return {"message": "Client data updated successfully"}


@client_router.get("", response_model=dict)
@exceptions_wrapper
async def get_all_clients(
    request: Request,
    access_token: str = Header(description="Access token"),
    client_service: ClientService = Depends(provide_client_service_stub)
    )->dict[str,list[dict[str, Any]]]:
    session = request.state.session
    client_service = ClientService(
        session=session, 
        client_repo=ClientRepository(session)
    )
    return{"all_clients": await client_service.get_all()}

@client_router.get("/{client_id}", response_model=dict)
@exceptions_wrapper
async def get_client(
    client_id:str,
    request: Request,
    client_service: ClientService = Depends(provide_client_service_stub)
    )->dict[str, Any]:
    session = request.state.session
    client_service = ClientService(
        session=session, 
        client_repo=ClientRepository(session)
    )
    return await client_service.get_client_by_client_id(client_id=client_id)


@client_router.delete("/{client_id}", status_code=status.HTTP_200_OK)
@exceptions_wrapper
async def delete_client(
    client_id:str,
    request: Request,
    client_service: ClientService = Depends(provide_client_service_stub)
    )->dict[str, Any]:
    session = request.state.session
    client_service = ClientService(
        session=session, 
        client_repo=ClientRepository(session)
    )
    if not await client_service.client_repo.validate_client_by_client_id(client_id=client_id):
        raise ClientNotFoundError
    await client_service.client_repo.delete_client_by_client_id(client_id=client_id)
    return {"message": "Client deleted successfully"}
