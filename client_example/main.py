from logging.config import dictConfig

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from client_example.api.middleware.auth_validation import (
    AuthorizationMiddleware,
)
from client_example.api.routers import auth, notes
from client_example.config.logging import LogConfig
from client_example.db import models
from client_example.db.database import engine

models.Base.metadata.create_all(bind=engine)
app = FastAPI()


dictConfig(LogConfig().to_dict)

app.include_router(notes.router)
app.include_router(auth.router)


# TODO set secret_key in env
app.add_middleware(AuthorizationMiddleware)
app.add_middleware(SessionMiddleware, secret_key="random-string")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
