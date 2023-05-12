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
class TestAdminUserEndpoint:
    async def setup_base(self, connection:AsyncSession, user_id: int = 1000) -> None:
        self.access_token = await JWTService().encode_jwt(
            payload={
                "stand": "CrazyDiamond",
                "aud":["admin"]
            }
        )
        self.group_repo = GroupRepository(connection)
        self.role_repo = RoleRepository(connection)

        self.user_repo = UserRepository(connection)
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

        await self.user_repo.create( 
            id=user_id,
            username="DioBrando",
            email = "theworld@timestop.com",
            email_confirmed = True,
            phone_number ="+20-123-123-123",
            phone_number_confirmed = False,
            two_factors_enabled = False,
        )
        await self.user_repo.change_password(
            user_id=user_id, password="WalkLikeAnEgiptian"
        )
        await connection.commit()
   
    async def setup_groups_roles(self, connection:AsyncSession) -> None:
        group_repo = GroupRepository(connection)
        groups:list[dict[str, Any]] = [
            {"name": "Polnareff", "parent_group": None},
            {"name": "Giorno", "parent_group": None},
        ]
        for group in groups:
            try:
                name = group["name"]
                parent_group = group["parent_group"]
                if type(name) is str and (parent_group is None or type(parent_group) is int):
                    await group_repo.create(
                            name=name,
                            parent_group=parent_group,
                        )
            except DuplicationError:
                if group["name"]:
                    logger.info(group["name"] + " group already exists")
                await connection.rollback()
        await connection.commit()
        groups = [
            {
                "name": "Gold",
                "parent_group": (
                    await group_repo.get_group_by_name(name="Giorno")
                ).id,
            },
            {
                "name": "Expirience",
                "parent_group": (
                    await group_repo.get_group_by_name(name="Giorno")
                ).id,
            },
            {
                "name": "Silver",
                "parent_group": (
                    await group_repo.get_group_by_name(name="Polnareff")
                ).id,
            },
            {
                "name": "Silver",
                "parent_group": (
                    await group_repo.get_group_by_name(name="Polnareff")
                ).id,
            },
        ]
        for group in groups:
            try:
                await group_repo.create(**group)
                await connection.commit()
            except DuplicationError:
                logger.info(group["name"] + " group already exists")
                await connection.rollback()

        groups = [
            {
                "name": "Reqiuem",
                "parent_group": (
                    await group_repo.get_group_by_name(name="Expirience")
                ).id,
            }
        ]
        for group in groups:
            try:
                await group_repo.create(**group)
                await connection.commit()
            except DuplicationError:
                if group["name"]:
                    logger.info(group["name"] + " group already exists")
                    await connection.rollback()

        role_repo = RoleRepository(connection)
        role_repo.delete
        for role in ("Standuser", "French", "Italian", "Vampire"):
            try:
                await role_repo.create(name=role)
            except DuplicationError:
                logger.info(role + " role already exists")

        await connection.commit()

    async def test_successful_get_all_users(self, connection:AsyncSession, client: AsyncClient) -> None:
        await self.setup_base(connection)
        headers = {
            "access-token": self.access_token,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        response = await client.request(
            "GET", "/administration/users", headers=headers
        )
        assert response.status_code == status.HTTP_200_OK

    async def test_successful_get_user(self, connection:AsyncSession, client: AsyncClient) -> None:
        user_id = 1000
        await self.setup_base(connection, user_id)
        headers = {"access-token": self.access_token}
        user_id = user_id
        response = await client.request(
            "GET",
            f"/administration/users/{user_id}",
            headers=headers,
        )
        assert response.status_code == status.HTTP_200_OK
        response_content = json.loads(response.content.decode("utf-8"))
        assert list(response_content.keys()) == [
            "username",
            "id",
            "phone_number",
            "phone_number_confirmed",
            "email",
            "email_confirmed",
            "lockout",
            "lockout_end_date_utc",
        ]

    async def test_successful_update_user(self, connection:AsyncSession, client: AsyncClient) -> None:
        user_id = 1000
        await self.setup_base(connection, user_id)
        headers = {
            "access-token": self.access_token,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        
        params: dict[str, Any] = {"username": "DiegoBrando"}
        response = await client.request(
            "PUT",
            f"/administration/users/{user_id}",
            headers=headers,
            data=params,
        )
        assert response.status_code == status.HTTP_200_OK
        response_content = json.loads(response.content.decode("utf-8"))

        response = await client.request(
            "GET",
            f"/administration/users/{user_id}",
            headers=headers,
        )
        response_content = json.loads(response.content.decode("utf-8"))
        assert response_content["username"] == "DiegoBrando"
        await self.user_repo.delete(user_id=1000)

    async def test_successful_delete_create_user(
        self, connection:AsyncSession, client: AsyncClient
    ) -> None:
        user_id = 1000
        await self.setup_base(connection, user_id)
        headers = {
            "access-token": self.access_token,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        response = await client.request(
            "DELETE",
            f"/administration/users/{user_id}",
            headers=headers,
        )
        assert response.status_code == status.HTTP_200_OK

        response = await client.request(
            "GET",
            f"/administration/users/{user_id}",
            headers=headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

        kwargs = {
            "username": "DioBrando",
            "security_stamp": "123",
            "email": "theworld@timestop.com",
            "phone_number": "+20-123-123-123",
            "two_factors_enabled": False,
        }
        headers = {
            "accept": "application/json",
            "access-token": self.access_token,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        response = await client.request(
            "POST",
            "/administration/users",
            headers=headers,
            data=kwargs,
        )
        assert response.status_code == status.HTTP_200_OK
        headers = {"access-token": self.access_token}
        response = await client.request(
            "GET", "/administration/users", headers=headers
        )

        response_content = json.loads(response.content.decode("utf-8"))
        for user in response_content["all_users"]:
            if user["username"] == "DioBrando":
                params = {"user_id": user["id"]}
                response = await client.request(
                    "DELETE",
                    "/administration/users/user_id",
                    headers=headers,
                    params=params,
                )
                break
        else:
            raise AssertionError

    async def test_successful_groups_users(self, connection:AsyncSession, client: AsyncClient) -> None:
        await self.setup_base(connection)
        await self.setup_groups_roles(connection)
        user_id = 1000
        headers = {
            "access-token": self.access_token,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "group_ids": f'{(await self.group_repo.get_group_by_name(name = "Polnareff")).id},{(await self.group_repo.get_group_by_name(name = "Silver")).id}',
        }

        response = await client.request(
            "POST",
            f"/administration/users/{user_id}/groups",
            headers=headers,
            data=data,
        )
        assert response.status_code == status.HTTP_200_OK

        headers = {"access-token": self.access_token}
        response = await client.request(
            "GET",
            f"/administration/users/{user_id}/groups",
            headers=headers,
        )
        assert response.status_code == status.HTTP_200_OK
        response_content = json.loads(response.content.decode("utf-8"))
        logger.info(response_content)
        assert len(response_content["groups"]) == 2

        headers = {
            "access-token": self.access_token,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        response = await client.request(
            "DELETE",
            f"/administration/users/{user_id}/groups",
            headers=headers,
            data=data,
        )
        assert response.status_code == status.HTTP_200_OK

        response = await client.request(
            "GET",
            f"/administration/users/{user_id}/groups",
            headers=headers,
        )
        assert response.status_code == status.HTTP_200_OK

        response_content = json.loads(response.content.decode("utf-8"))
        logger.info(response_content)
        assert len(response_content["groups"]) == 0

    async def test_successful_roles_users(self, connection:AsyncSession, client: AsyncClient) -> None:
        await self.setup_base(connection)
        await self.setup_groups_roles(connection)
        user_id = 1000
        headers = {
            "access-token": self.access_token,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "role_ids": f'{(await self.role_repo.get_role_by_name(name = "Standuser")).id},{(await self.role_repo.get_role_by_name(name = "Vampire")).id}',
        }

        response = await client.request(
            "POST", f"/administration/users/{user_id}/roles", headers=headers, data=data
        )
        assert response.status_code == status.HTTP_200_OK

        headers = {"access-token": self.access_token}
        response = await client.request(
            "GET",
            f"/administration/users/{user_id}/roles",
            headers=headers,
        )
        assert response.status_code == status.HTTP_200_OK
        response_content = json.loads(response.content.decode("utf-8"))
        logger.info(response_content)
        assert len(response_content["roles"]) == 2

        headers = {
            "access-token": self.access_token,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        response = await client.request(
            "DELETE",
            f"/administration/users/{user_id}/roles",
            headers=headers,
            data=data,
        )
        assert response.status_code == status.HTTP_200_OK

        headers = {"access-token": self.access_token}
        response = await client.request(
            "GET",
            f"/administration/users/{user_id}/roles",
            headers=headers,
        )
        assert response.status_code == status.HTTP_200_OK

        response_content = json.loads(response.content.decode("utf-8"))
        logger.info(response_content)
        a = len(response_content["roles"])
        assert a == 0

    async def test_successful_password_change(
        self, connection:AsyncSession, client: AsyncClient
    ) -> None:
        await self.setup_base(connection)
        user_id = 1000
        headers = {
            "access-token": self.access_token,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {"new_password": "muda_muda_muda"}
        password_one = (await self.user_repo.get_user_by_id(1000)).password_hash.value

        response = await client.request(
            "PUT",
            f"/administration/users/{user_id}/password",
            headers=headers,
            data=data,
        )
        assert response.status_code == 200
        password_two = (
            await self.user_repo.get_user_by_id(1000)
        ).password_hash.value
        assert password_two != password_one
