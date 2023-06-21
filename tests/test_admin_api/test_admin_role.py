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
from sqlalchemy import exc
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from typing import Any


logger = logging.getLogger(__name__)


@pytest.mark.usefixtures("engine", "pre_test_setup")
@pytest.mark.asyncio
class TestAdminRoleEndpoint:
    async def setup_base(
        self, connection: AsyncSession, user_id: int = 1000
    ) -> None:
        self.access_token = await JWTService().encode_jwt(
            payload={"stand": "CrazyDiamond", "aud": ["admin"]}
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
            email="theworld@timestop.com",
            email_confirmed=True,
            phone_number="+20-123-123-123",
            phone_number_confirmed=False,
            two_factors_enabled=False,
        )
        await self.user_repo.change_password(
            user_id=user_id, password="WalkLikeAnEgiptian"
        )
        await connection.commit()

    async def setup_groups_roles(self, connection: AsyncSession) -> None:
        group_repo = GroupRepository(connection)
        groups: list[dict[str, Any]] = [
            {"name": "Polnareff", "parent_group": None},
            {"name": "Giorno", "parent_group": None},
        ]
        for group in groups:
            try:
                name = group["name"]
                parent_group = group["parent_group"]
                if type(name) is str and (
                    parent_group is None or type(parent_group) is int
                ):
                    await group_repo.create(
                        name=name,
                        parent_group=parent_group,
                    )
            except exc.IntegrityError:
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
            except exc.IntegrityError:
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
            except exc.IntegrityError:
                if group["name"]:
                    logger.info(group["name"] + " group already exists")
                    await connection.rollback()

        role_repo = RoleRepository(connection)
        role_repo.delete
        for role in ("Standuser", "French", "Italian", "Vampire"):
            try:
                await role_repo.create(name=role)
            except exc.IntegrityError:
                logger.info(role + " role already exists")

        await connection.commit()

    async def test_get_role(
        self, connection: AsyncSession, client: AsyncClient
    ) -> None:
        await self.setup_base(connection)
        await self.setup_groups_roles(connection)

        headers = {
            "access-token": self.access_token,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        role_id = (await self.role_repo.get_role_by_name("Standuser")).id

        response = await client.request(
            "GET",
            f"/administration/roles/{role_id}",
            headers=headers,
        )
        assert response.status_code == status.HTTP_200_OK
        response_content = json.loads(response.content.decode("utf-8"))
        logger.info(response_content)
        assert response_content["role"]["name"] == "Standuser"

    async def test_get_all_roles(
        self, connection: AsyncSession, client: AsyncClient
    ) -> None:
        await self.setup_base(connection)
        await self.setup_groups_roles(connection)

        headers = {
            "access-token": self.access_token,
            "Content-Type": "application/x-www-form-urlencoded",
        }

        response = await client.request(
            "GET", "/administration/roles", headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        response_content = json.loads(response.content.decode("utf-8"))
        logger.info(response_content)
        assert len(response_content["all_roles"])

    async def test_delete_role(
        self, connection: AsyncSession, client: AsyncClient
    ) -> None:
        await self.setup_base(connection)
        await self.setup_groups_roles(connection)

        headers = {
            "access-token": self.access_token,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        role_id = (await self.role_repo.get_role_by_name(name="Standuser")).id

        response = await client.request(
            "DELETE",
            f"/administration/roles/{role_id}",
            headers=headers,
        )
        assert response.status_code == status.HTTP_200_OK
        headers = {"access-token": self.access_token}
        response = await client.request(
            "GET",
            f"/administration/roles/{role_id}",
            headers=headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_create_update_role(
        self, connection: AsyncSession, client: AsyncClient
    ) -> None:
        await self.setup_base(connection)
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
            "/administration/roles",
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
            "name": "Ultimate Life Form",
        }
        role_id = (await self.role_repo.get_role_by_name("Pillar Man")).id
        response = await client.request(
            "PUT",
            f"/administration/roles/{role_id}",
            headers=headers,
            data=params,
        )
        assert response.status_code == status.HTTP_200_OK
        assert await self.role_repo.get_role_by_name("Ultimate Life Form")
        await self.role_repo.delete(
            (await self.role_repo.get_role_by_name("Ultimate Life Form")).id
        )
