from fastapi import APIRouter, Form, Depends
from fastapi.responses import RedirectResponse

from src.presentation.models.authorization import RequestModel
from src.business_logic.services import get_authorise, AuthorisationService


auth_router = APIRouter(
    prefix='/authorize',
)


@auth_router.get('/', status_code=302, tags=['Authorization'])
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
        auth_class: AuthorisationService = Depends()
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
        acr_values=acr_values
    )
    auth_class = auth_class
    auth_class.set_request_model(request=request)
    firmed_redirect_uri = await auth_class.get_redirect_url()
    response = RedirectResponse(firmed_redirect_uri, status_code=302)

    return response


@auth_router.post('/', status_code=302, tags=['Authorization'])
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
        auth_class: AuthorisationService = Depends()
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
        acr_values=acr_values
    )

    auth_class = auth_class
    auth_class.set_request_model(request=request)
    firmed_redirect_uri = await auth_class.get_redirect_url()
    response = RedirectResponse(firmed_redirect_uri, status_code=302)

    return response
