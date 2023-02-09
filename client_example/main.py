from logging.config import dictConfig

from fastapi import FastAPI

from client_example.config.logging import LogConfig
from client_example.middleware.auth_validation import AuthorizationMiddleware
from client_example.routers import auth, notes

from . import models
from .database import engine

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

dictConfig(LogConfig().to_dict)

app.include_router(notes.router)
app.include_router(auth.router)
app.add_middleware(AuthorizationMiddleware)
