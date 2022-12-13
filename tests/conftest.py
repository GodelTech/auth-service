import pytest_asyncio
from fastapi import FastAPI

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncIterator

from src.main import get_application


@pytest_asyncio.fixture
async def app() -> FastAPI:
    return get_application()


@pytest_asyncio.fixture
async def connection(app: FastAPI) -> AsyncIterator[AsyncSession]:
    async with app.container.db().session_factory() as conn:
        yield conn


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(
        app=app,
        base_url="http://testserver",
        headers={"Content-Type": "application/json"},
    ) as client:
        yield client
