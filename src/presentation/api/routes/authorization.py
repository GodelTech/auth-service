from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse

from src.presentation.api.models import RequestModel, DataRequestModel
from src.business_logic.services import AuthorisationService


auth_router = APIRouter(
    prefix='/authorize',
)


@auth_router.get('/', status_code=302, tags=['Authorization'])
async def get_authorize(
        request_model: RequestModel = Depends(),
        auth_class: AuthorisationService = Depends(),
):

    auth_class = auth_class
    auth_class.request = request_model
    firmed_redirect_uri = await auth_class.get_redirect_url()
    response = RedirectResponse(firmed_redirect_uri, status_code=302)

    return response


@auth_router.post('/', status_code=302, tags=['Authorization'])
async def post_authorize(
        request_body: DataRequestModel = Depends(),
        auth_class: AuthorisationService = Depends()
):

    request = RequestModel(**request_body.__dict__)
    auth_class = auth_class
    auth_class.request = request
    firmed_redirect_uri = await auth_class.get_redirect_url()
    response = RedirectResponse(firmed_redirect_uri, status_code=302)

    return response
