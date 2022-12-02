from fastapi import APIRouter, Depends

from src.presentation.models.authorization import PostRequestModel, ResponseAuthorizationModel
from src.business_logic.services.authorisation_services import get_authorise
from src.data_access.postgresql.repositories.client import ClientRepository
from src.data_access.postgresql.repositories.user import UserRepository
from src.data_access.postgresql.repositories.persistent_grant import PersistentGrantRepository

from src.business_logic.dependencies.database import get_repository


auth_router = APIRouter(
    prefix='/authorize',
)


@auth_router.get('/', response_model=bool, status_code=302)
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
    if await get_authorise(
            client_id=client_id,
            response_type=response_type,
            scope=scope,
            redirect_uri=redirect_uri,
            client_repo=client_repo,
            user_repo=user_repo,
            persistent_grant_repo=persistent_grant_repo
    ):
        result = True
    else:
        result = False

    # result = await get_authorisation_get(client_id=client_id, repo=client_repo)
    return result

# response_model=ResponseAuthorizationModel


@auth_router.post('/', response_model=bool, status_code=302)
async def post_authorize(
        request_body: PostRequestModel,
        client_repo: ClientRepository = Depends(get_repository(ClientRepository))
):

    if await get_authorise(client_id=request_body.client_id, scope=request_body.scope, client_repo=client_repo):
        result = True
    else:
        result = False

    return result

