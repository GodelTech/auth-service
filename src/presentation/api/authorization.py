from fastapi import APIRouter

from src.presentation.models.authorization import PostRequestModel, ResponseAuthorizationModel
from src.business_logic.services.authorisation_services import get_authorisation


auth_router = APIRouter(
    prefix='/authorization',
)


@auth_router.get('/', response_model=ResponseAuthorizationModel)
def get_authorize(
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
        acr_values: str = None
):
    data = {
        "code": "giberjuber",
        "state": "not so bad"
    }

    result = get_authorisation(data)
    # result = ResponseAuthorizationModel(code=code, state=state)
    return result


@auth_router.post('/', response_model=ResponseAuthorizationModel)
def post_authorize(request_body: PostRequestModel):
    result = ResponseAuthorizationModel(code='Code', state='State')

    return result
