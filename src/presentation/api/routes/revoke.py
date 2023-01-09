from fastapi import APIRouter, Depends, HTTPException, Request
from src.business_logic.services.tokens import TokenService
from src.presentation.api.models.revoke import RequestRevokeModel, BodyRequestRevokeModel
import logging

logger = logging.getLogger('is_app')

revoke_router = APIRouter(
    prefix='/revoke',
)


@revoke_router.post('/', status_code= 200, tags=['Revoke'])
async def post_revoke_token(request:Request ,request_model: RequestRevokeModel = Depends(), request_body : BodyRequestRevokeModel= Depends(), token_class: TokenService = Depends()):
    try:
    
        token_class = token_class
        token_class.request = request
        token_class.request_headers = request_model
        token_class.request_body= request_body
        
        logger.info(f'Revoking for token {request_body.token} started')
        return await token_class.revoke_token()

    except:
        raise HTTPException(status_code=403, detail="Incorrect Token")