import json
import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from src.business_logic.services.jwt_token import JWTService
from src.data_access.postgresql.tables.persistent_grant import PersistentGrant
from src.data_access.postgresql.repositories.user import UserRepository
from src.data_access.postgresql.repositories.groups import GroupRepository
from src.data_access.postgresql.repositories.roles import RoleRepository
import logging
from src.data_access.postgresql.errors.user import DuplicationError
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from typing import Any


logger = logging.getLogger(__name__)


@pytest.mark.asyncio
class TestUserEndpoint:
    async def setup_base(self, engine: AsyncEngine, user_id: int = 1000) -> None:
        self.access_token = await JWTService().encode_jwt(
            payload={
                "stand": "CrazyDiamond",
                "aud":["admin"]
            }
        )
        self.user_repo = UserRepository(engine)


    async def test_successful_get_HTML_register(self, engine: AsyncEngine, client: AsyncClient) -> None:
       #  await self.setup_base(engine)
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        response = await client.request(
            "GET", "/user/register/profile", headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        response_content = response.content.decode("utf-8")
        assert "<h1>Registration Form</h1>" in response_content
        assert '<input type="text" id="name" name="name" required>' in response_content

        response = await client.request(
            "GET", "/user/register/openid", headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        response_content = response.content.decode("utf-8")
        assert "<h1>Registration Form</h1>" in response_content
        assert '<input type="text" id="name" name="name" required>' not in response_content

    async def test_successful_post_register_post_add_info(self, engine: AsyncEngine, client: AsyncClient) -> None:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "username": "polnareff",
            "email":"polnareff@mail",
            "password":"polnareff",
            # "name":"polnareff",
            # "given_name":"polnareff",
            # "family_name":"polnareff",
            # "middle_name":"polnareff",
            # "preferred_username":"polnareff",
            # "profile":"polnareff",
            "picture":"polnareff",
            "website":"polnareff",
            "gender":"polnareff",
            # "birthdate":"12/12/1212",
            # "zoneinfo":"ZTM1",
            # "phone_number":"123123132",
            # "address":"polnareff",
            }
        response = await client.request(
            "POST", "/user/register", headers=headers, data=data
        )
        assert response.status_code == status.HTTP_200_OK
        response_content = response.content.decode("utf-8")
        user_repo = UserRepository(engine)
        user = await user_repo.get_user_by_username("polnareff")
        assert '<h1>OIDC Registration Success</h1>' in response_content

        data = {
            "name":"polnareff",
            "given_name":"polnareff",
            "family_name":"polnareff",
            "middle_name":"polnareff",
            "preferred_username":"polnareff",
            "profile":"polnareff",
            }
        response = await client.request(
            "POST", "/user/add_info", headers=headers, data=data
        )
        assert response.status_code == status.HTTP_200_OK
        assert user_repo.get_claims(user.id)