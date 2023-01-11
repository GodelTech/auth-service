from fastapi import APIRouter, Depends, HTTPException, Request, Header
from src.business_logic.services.tokens import TokenService
from src.presentation.api.models.revoke import BodyRequestRevokeModel
import logging

logger = logging.getLogger('is_app')

revoke_router = APIRouter(
    prefix='/revoke',
)


@revoke_router.post('/', status_code= 200, tags=['Revoke'])
async def post_revoke_token(
    request:Request, 
    auth_swagger: str | None = Header(default=None, description="Authorization"),
    request_body : BodyRequestRevokeModel= Depends(), 
    token_class: TokenService = Depends()
    ):

    try:
        token_class = token_class
        token_class.request = request
        
        token = request.headers.get('authorization')

        if token != None:
            token_class.authorization = token
        elif auth_swagger != None:
            token_class.authorization = auth_swagger
        else:
            raise Exception
        
        token_class.request_body= request_body

        logger.info(f'Revoking for token {request_body.token} started')
        return await token_class.revoke_token()

    except:
        raise HTTPException(status_code=403, detail="Incorrect Token")