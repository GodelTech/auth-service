from fastapi import APIRouter, Depends, Form
from starlette import status

from src.presentation.models.authorization import RequestModel, ResponseAuthorizationModel
from src.business_logic.services.authorisation_services import get_authorise
from src.data_access.postgresql.repositories.client import ClientRepository
from src.data_access.postgresql.repositories.user import UserRepository
from src.data_access.postgresql.repositories.persistent_grant import PersistentGrantRepository

from src.business_logic.dependencies.database import get_repository


auth_router = APIRouter(
    prefix='/authorize',
)


@auth_router.get('/', response_model=ResponseAuthorizationModel, status_code=302, tags=['Authorization'])
async def get_authorize(
        client_id: str,
        response_type: str,
        scope: str,
        redirect_uri: str,
        state: str = None,
        response_mode: str = None,
        nonce: str = None,
        display: str = None,
        prompt: str = None,
        max_age: int = None,
        ui_locales: str = None,
        id_token_hint: str = None,
        login_hint: str = None,
        acr_values: str = None,
        client_repo: ClientRepository = Depends(get_repository(ClientRepository)),
        user_repo: UserRepository = Depends(get_repository(UserRepository)),
        persistent_grant_repo: PersistentGrantRepository = Depends(get_repository(PersistentGrantRepository))
):
    request = RequestModel(
        client_id=client_id,
        response_type=response_type,
        scope=scope,
        redirect_uri=redirect_uri,
        state=state,
        response_mode=response_mode,
        nonce=nonce,
        display=display,
        prompt=prompt,
        max_age=max_age,
        ui_locales=ui_locales,
        id_token_hint=id_token_hint,
        login_hint=login_hint,
        acr_values=acr_values,
        client_repo=client_repo,
        user_repo=user_repo,
        persistent_grant_repo=persistent_grant_repo
    )
    try:
        response = await get_authorise(
            request=request,
            client_repo=client_repo,
            user_repo=user_repo,
            persistent_grant_repo=persistent_grant_repo
        )
        return response
    except:
        status_code = status.HTTP_403_FORBIDDEN
        return status_code


@auth_router.post('/', response_model=ResponseAuthorizationModel, status_code=302, tags=['Authorization'])
async def post_authorize(
        client_id: str = Form(),
        response_type: str = Form(),
        scope: str = Form(),
        redirect_uri: str = Form(),
        state: str = Form(None),
        response_mode: str = Form(None),
        nonce: str = Form(None),
        display: str = Form(None),
        prompt: str = Form(None),
        max_age: int = Form(None),
        ui_locales: str = Form(None),
        id_token_hint: str = Form(None),
        login_hint: str = Form(None),
        acr_values: str = Form(None),
        client_repo: ClientRepository = Depends(get_repository(ClientRepository)),
        user_repo: UserRepository = Depends(get_repository(UserRepository)),
        persistent_grant_repo: PersistentGrantRepository = Depends(get_repository(PersistentGrantRepository))
):
    request = RequestModel(
        client_id=client_id,
        response_type=response_type,
        scope=scope,
        redirect_uri=redirect_uri,
        state=state,
        response_mode=response_mode,
        nonce=nonce,
        display=display,
        prompt=prompt,
        max_age=max_age,
        ui_locales=ui_locales,
        id_token_hint=id_token_hint,
        login_hint=login_hint,
        acr_values=acr_values,
        client_repo=client_repo,
        user_repo=user_repo,
        persistent_grant_repo=persistent_grant_repo
    )
    try:
        response = await get_authorise(
            request=request,
            client_repo=client_repo,
            user_repo=user_repo,
            persistent_grant_repo=persistent_grant_repo
        )
        return response
    except:
        status_code = status.HTTP_403_FORBIDDEN
        return status_code
