import logging
from pydantic import ValidationError
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Any, Union
from src.data_access.postgresql.errors import *
from jwt.exceptions import PyJWTError
logger = logging.getLogger(__name__)


class ExceptionsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: Any):
        self.app = app

    async def dispatch_func(self, request: Request, call_next:Callable[..., Any]) -> Any:
        try:
            response = await call_next(request)
            return response
        except ClientNotFoundError:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, 
                content="Client not found"
            )
        except (ValidationError):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST, 
                content="BAD_REQUEST"
            )
        except ClaimsNotFoundError:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content="You don't have permission for this claims",
            )
        except (ValueError, PyJWTError):
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, 
                content="Not found"
            )
        except DuplicationError:
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT, 
                content="Duplication"
            )
        except (IncorrectAuthTokenError, KeyError):
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content="Incorrect Token",
            )
        except:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content="INTERNAL_SERVER_ERROR",
            )

