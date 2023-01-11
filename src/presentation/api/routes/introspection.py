from fastapi import APIRouter, Depends, HTTPException, Request, Header
from src.business_logic.services.introspection import IntrospectionServies 
from src.presentation.api.models.introspection import ResponceIntrospectionModel, RequestIntrospectionModel, BodyRequestIntrospectionModel
import logging

logger = logging.getLogger('is_app')

introspection_router = APIRouter(
    prefix='/introspection',
)


@introspection_router.post('/', response_model = ResponceIntrospectionModel, tags=['Introspection'])
async def post_introspection(
     request:Request , 
     auth_swagger: str | None = Header(default=None, description="Authorization"), 
     request_body : BodyRequestIntrospectionModel= Depends(), 
     introspection_class: IntrospectionServies = Depends()):
     try:
        introspection_class = introspection_class
        introspection_class.request = request
        
        token = request.headers.get('authorization')
        if token != None:
            introspection_class.authorization = token
        elif auth_swagger != None:
            introspection_class.authorization = auth_swagger
        else:
            raise ValueError

        introspection_class.request_body= request_body
        
        logger.info(f'Introspection for token {request_body.token} started')
        return await introspection_class.analyze_token()

     except:
        raise HTTPException(status_code=403, detail="Incorrect Authorization Token")