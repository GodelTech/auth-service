from fastapi import APIRouter, Depends, HTTPException, Request, Header, status
from src.business_logic.services.introspection import IntrospectionServies 
from src.presentation.api.models.introspection import ResponceIntrospectionModel, BodyRequestIntrospectionModel
import logging
from typing import Union
from jwt.exceptions import ExpiredSignatureError

logger = logging.getLogger('is_app')

introspection_router = APIRouter(
    prefix='/introspection',
)


@introspection_router.post('/', response_model = ResponceIntrospectionModel, tags=['Introspection'])
async def post_introspection(
    request:Request , 
    auth_swagger: Union[str, None] = Header(default=None, description="Authorization"),  #crutch for swagger
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
            raise PermissionError

        introspection_class.request_body = request_body
        logger.info(f'Introspection for token {request_body.token} started')
        return await introspection_class.analyze_token()

    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect Token")

    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect Token")
    
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
