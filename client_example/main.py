from fastapi import FastAPI

from client_example.middleware.auth_validation import AuthorizationMiddleware
from client_example.routers import auth, notes

from . import models
from .database import engine

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(notes.router)
app.include_router(auth.router)
app.add_middleware(AuthorizationMiddleware)
