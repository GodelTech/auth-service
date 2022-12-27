from fastapi import APIRouter, Depends, HTTPException, Request
from src.business_logic.services.tokens import TokenService
from src.presentation.api.models.revoke import RequestRevokeModel, BodyRequestRevokeModel
import logging

logger = logging.getLogger('is_app')

revoke_router = APIRouter(
    prefix='/revoke',
)

'''
When 'TokenService' will be ready add to it a method:

async def revoke_token(self, token):
        decoded_token = self.jwt_service.decode_token(token)
        if await self.persistent_grant_repo.exists(grant_type=decoded_token["grant_type"], data=decoded_token["data"], key=decoded_token["key"]):
            self.persistent_grant_repo.delete_grant(
                grant_type=decoded_token["grant_type"], data=decoded_token["data"], key=decoded_token["key"])

        else:
            raise ValueError

'''


@revoke_router.post('/', status_code= 200, tags=['Revoke'])
async def post_revoke_token(request:Request ,request_model: RequestRevokeModel = Depends(), request_body : BodyRequestRevokeModel= Depends(), revoke_class: TokenService = Depends()):
    try:
    
        revoke_class = revoke_class
        revoke_class.request = request
        revoke_class.request_headers = request_model
        revoke_class.request_body= request_body
        
        logger.info(f'Introspection for token {request_body.token} started')
        return await revoke_class.analyze_token()

    except:
        raise HTTPException(status_code=403, detail="Incorrect Authorization Token")