import json
import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import insert, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.business_logic.services.jwt_token import JWTService
from src.data_access.postgresql.tables.persistent_grant import PersistentGrant
from src.data_access.postgresql.repositories.user import UserRepository
from src.data_access.postgresql.repositories.groups import GroupRepository
from src.data_access.postgresql.repositories.roles import RoleRepository
import logging
from sqlalchemy import exc
from typing import Any


logger = logging.getLogger(__name__)


@pytest.mark.asyncio
class TestAdminGroupEndpoint:
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

    async def test_get_group(self, connection: AsyncSession, client: AsyncClient) -> None:
        await self.setup_base(connection)
        await self.setup_groups_roles(connection)
        
        headers = {
            "access-token": self.access_token,
            "Content-Type": "application/x-www-form-urlencoded",
        }
       
        group_id=(await self.group_repo.get_group_by_name("Polnareff")).id
        
        response = await client.request(
            "GET",
            f"/administration/groups/{group_id}",
            headers=headers,
        )
        assert response.status_code == status.HTTP_200_OK
        response_content = json.loads(response.content.decode("utf-8"))
        logger.info(response_content)
        assert response_content["name"] == "Polnareff"

    async def test_get_all_group(self, connection: AsyncSession, client: AsyncClient) -> None:
        await self.setup_base(connection)
        await self.setup_groups_roles(connection)

        headers = {
            "access-token": self.access_token,
            "Content-Type": "application/x-www-form-urlencoded",
        }

        response = await client.request(
            "GET", "/administration/groups", headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        response_content = json.loads(response.content.decode("utf-8"))
        logger.info(response_content)
        assert len(response_content["all_groups"]) >= 6

    async def test_get_subgroups(self, connection: AsyncSession, client: AsyncClient) -> None:
        await self.setup_base(
            connection,
        )
        await self.setup_groups_roles(connection)

        headers = {
            "access-token": self.access_token,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        
        group_id = (await self.group_repo.get_group_by_name(name="Giorno")).id

        response = await client.request(
            "GET",
            f"/administration/groups/{group_id}/subgroups",
            headers=headers,
        )
        assert response.status_code == status.HTTP_200_OK
        response_content = json.loads(response.content.decode("utf-8"))
        logger.info(response_content)
        for group in list(response_content.values())[0]:
            if group["subgroups"] is not None:
                break
        else:
            raise AssertionError

    async def test_delete_group(self, connection: AsyncSession, client: AsyncClient) -> None:
        await self.setup_base(
            connection,
        )
        await self.setup_groups_roles(connection)

        headers = {
            "access-token": self.access_token,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        group_id = (await self.group_repo.get_group_by_name(name="Giorno")).id

        response = await client.request(
            "DELETE",
            f"/administration/groups/{group_id}",
            headers=headers,
        )
        assert response.status_code == status.HTTP_200_OK
        headers = {"access-token": self.access_token}
        response = await client.request(
            "GET",
            f"/administration/groups/{group_id}",
            headers=headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_create_update_group(self, connection: AsyncSession, client: AsyncClient) -> None:
        await self.setup_base(
            connection,
        )
        try:
            await self.group_repo.delete(
                (await self.group_repo.get_group_by_name("Diavolo")).id
            )
        except:
            pass
        headers = {
            "access-token": self.access_token,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        params = {"name": "Diavolo"}

        response = await client.request(
            "POST",
            "/administration/groups",
            headers=headers,
            data=params,
        )
        assert response.status_code == status.HTTP_200_OK

        headers = {
            "access-token": self.access_token,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        params = {
            "name": "Doppio",
        }
        group_id = (await self.group_repo.get_group_by_name("Diavolo")).id
        response = await client.request(
            "PUT",
            f"/administration/groups/{group_id}",
            headers=headers,
            data=params,
        )
        assert response.status_code == status.HTTP_200_OK

        await self.group_repo.delete(
            (await self.group_repo.get_group_by_name("Doppio")).id
        )
