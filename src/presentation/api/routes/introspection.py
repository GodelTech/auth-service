from fastapi import APIRouter, Depends, HTTPException, Request
from src.business_logic.services.introspection import IntrospectionServies 
from src.presentation.api.models.introspection import ResponceIntrospectionModel, RequestIntrospectionModel, BodyRequestIntrospectionModel
import logging

logger = logging.getLogger('is_app')

introspection_router = APIRouter(
    prefix='/introspection',
)


@introspection_router.post('/', response_model = ResponceIntrospectionModel, tags=['Introspection'])
async def post_introspection(request:Request ,request_model: RequestIntrospectionModel = Depends(), request_body : BodyRequestIntrospectionModel= Depends(), introspection_class: IntrospectionServies = Depends()):
   # try:
    
        introspection_class = introspection_class
        introspection_class.request = request
        introspection_class.request_headers = request_model
        introspection_class.request_body= request_body
        
        logger.info(f'Introspection for token {request_body.token} started')
        return await introspection_class.analyze_token()

   # except:
        raise HTTPException(status_code=403, detail="Incorrect Authorization Token")