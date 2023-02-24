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

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
class TestAdminRoleEndpoint:
    async def setup_base(self, engine, user_id: int = 1000):
        self.access_token = await JWTService().encode_jwt(
            payload={"stand": "CrazyDiamond"}
        )
        self.group_repo = GroupRepository(engine)
        self.role_repo = RoleRepository(engine)

        self.user_repo = UserRepository(engine)
        try:
            if await self.user_repo.exists(user_id=user_id):
                await self.user_repo.delete(user_id=user_id)
            if await self.user_repo.get_user_by_username(username="DioBrando"):
                await self.user_repo.delete(
                    user_id=(
                        await self.user_repo.get_user_by_username(
                            username="DioBrando"
                        )
                    ).id
                )
        except:
            pass

        data = {
            "id": user_id,
            "username": "DioBrando",
            "email": "theworld@timestop.com",
            "email_confirmed": True,
            "phone_number": "+20-123-123-123",
            "phone_number_confirmed": False,
           # "password_hash": "1",
            "two_factors_enabled": False,
        }
        await self.user_repo.create(**data)

    async def setup_roles(self, engine):
        role_repo = RoleRepository(engine)
        role_repo.delete
        for role in ("Standuser", "French", "Italian", "Vampire"):
            try:
                await role_repo.create(name=role)
            except DuplicationError:
                logger.info(role + " role already exists")

    async def test_get_role(self, engine, client: AsyncClient):
        await self.setup_base(
            engine,
        )
        await self.setup_roles(engine)

        headers = {
            "access-token": self.access_token,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        params = {
            "role_id": (await self.role_repo.get_role_by_name("Standuser")).id
        }

        response = await client.request(
            "GET",
            "/administration/role/get_role",
            headers=headers,
            params=params,
        )
        assert response.status_code == status.HTTP_200_OK
        response_content = json.loads(response.content.decode("utf-8"))
        logger.info(response_content)
        assert response_content["role"]["name"] == "Standuser"

    async def test_get_all_roles(self, engine, client: AsyncClient):
        await self.setup_base(
            engine,
        )
        await self.setup_roles(engine)

        headers = {
            "access-token": self.access_token,
            "Content-Type": "application/x-www-form-urlencoded",
        }

        response = await client.request(
            "GET", "/administration/role/get_all_roles", headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        response_content = json.loads(response.content.decode("utf-8"))
        logger.info(response_content)
        assert len(response_content["all_roles"])

    async def test_get_roles(self, engine, client: AsyncClient):
        await self.setup_base(
            engine,
        )
        await self.setup_roles(engine)

        headers = {
            "access-token": self.access_token,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        params = {
            "role_ids": f'{(await self.role_repo.get_role_by_name(name = "Standuser")).id},{(await self.role_repo.get_role_by_name(name = "Vampire")).id}'
        }

        response = await client.request(
            "GET",
            "/administration/role/get_roles",
            headers=headers,
            params=params,
        )
        assert response.status_code == status.HTTP_200_OK
        response_content = json.loads(response.content.decode("utf-8"))
        logger.info(response_content)
        for role in list(response_content.values())[0]:
            if role["name"] not in ("Standuser", "Vampire"):
                raise AssertionError

    async def test_delete_role(self, engine, client: AsyncClient):
        await self.setup_base(
            engine,
        )
        await self.setup_roles(engine)

        headers = {
            "access-token": self.access_token,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        params = {
            "role_id": (
                await self.role_repo.get_role_by_name(name="Standuser")
            ).id
        }

        response = await client.request(
            "DELETE",
            "/administration/role/delete_role",
            headers=headers,
            data=params,
        )
        assert response.status_code == status.HTTP_200_OK
        headers = {"access-token": self.access_token}
        response = await client.request(
            "GET",
            "/administration/role/get_role",
            headers=headers,
            params=params,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_create_update_role(self, engine, client: AsyncClient):
        await self.setup_base(
            engine,
        )
        try:
            await self.role_repo.delete(
                (await self.role_repo.get_role_by_name("Pillar Man")).id
            )
        except:
            pass
        try:
            await self.role_repo.delete(
                (await self.role_repo.get_role_by_name("Ultimate Life Form")).id
            )
        except:
            pass

        headers = {
            "access-token": self.access_token,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        params = {"name": "Pillar Man"}

        response = await client.request(
            "POST",
            "/administration/role/new_role",
            headers=headers,
            data=params,
        )
        assert response.status_code == status.HTTP_200_OK
        assert await self.role_repo.get_role_by_name("Pillar Man")
        headers = {
            "access-token": self.access_token,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        params = {
            "role_id": (await self.role_repo.get_role_by_name("Pillar Man")).id,
            "name": "Ultimate Life Form",
        }

        response = await client.request(
            "PUT",
            "/administration/role/update_role",
            headers=headers,
            data=params,
        )
        assert response.status_code == status.HTTP_200_OK
        assert await self.role_repo.get_role_by_name("Ultimate Life Form")
        await self.role_repo.delete(
            (await self.role_repo.get_role_by_name("Ultimate Life Form")).id
        )
