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

logger = logging.getLogger("is_app")

@pytest.mark.asyncio
class TestAdminUserEndpoint:

    async def setup_base(self, engine, user_id:int = 1000): 
        self.access_token = await JWTService().encode_jwt(payload={"stand":"CrazyDiamond"})
        self.group_repo = GroupRepository(engine)
        self.role_repo = RoleRepository(engine)

        self.user_repo = UserRepository(engine)
        try:
            if await self.user_repo.exists(user_id = user_id):
                await self.user_repo.delete(user_id = user_id)
            if await self.user_repo.get_user_by_username(username="DioBrando"):
                await self.user_repo.delete(user_id = (await self.user_repo.get_user_by_username(username="DioBrando")).id)
        except:
            pass

        data = {
            "id": user_id,
            "username":"DioBrando",
            "email":"theworld@timestop.com", 
            "email_confirmed": True, 
            "phone_number":"+20-123-123-123",
            "phone_number_confirmed": False,
            "password_hash": "1",
            "two_factors_enabled":False,
        }
        await self.user_repo.create(**data)

    async def setup_groups_roles(self, engine): 
        await self.setup_base(engine)
        group_repo = GroupRepository(engine)
        groups = [
            {
                "name": "Polnareff",
                "parent_group": None
            },
            {
                "name": "Giorno",
                "parent_group": None
            },]
        for group in groups:
            try:
                await group_repo.create(**group)
            except DuplicationError:
                logger.info(group["name"] + " group already exists")

        groups = [
            {
                "name": "Gold",
                "parent_group": (await group_repo.get_group_by_name(name = "Giorno")).id
            },
            {
                "name": "Expirience",
                "parent_group": (await group_repo.get_group_by_name(name = "Giorno")).id
            },
            {
                "name": "Silver",
                "parent_group": (await group_repo.get_group_by_name(name = "Polnareff")).id
            },
            {
                "name": "Silver",
                "parent_group": (await group_repo.get_group_by_name(name = "Polnareff")).id
            },]
        for group in groups:
            try:
                await group_repo.create(**group)
            except DuplicationError:
                logger.info(group["name"] + " group already exists")

        groups = [
            {
                "name":"Reqiuem",
                "parent_group": (await group_repo.get_group_by_name(name = "Expirience")).id
            }
            ]
        for group in groups:
            try:
                await group_repo.create(**group)
            except DuplicationError:
                logger.info(group["name"] + " group already exists")

        role_repo = RoleRepository(engine)
        role_repo.delete
        for role in ("Standuser", "French", "Italian", "Vampire"):
            try:
                await role_repo.create(name = role)
            except DuplicationError:
                logger.info(role + " role already exists")

    async def test_successful_get_all_users(self, engine, client: AsyncClient):
        await self.setup_base(engine)
        headers = {
            "access-token" : self.access_token,
            "Content-Type": "application/x-www-form-urlencoded"
            }
        response = await client.request("GET", "/administration/user/all_users", headers=headers)
        assert response.status_code == status.HTTP_200_OK
    
    async def test_successful_get_user(self, engine, client: AsyncClient):
        user_id = 1000
        await self.setup_base(engine, user_id)
        headers = {"access-token" : self.access_token}
        params = {"user_id":user_id}
        response = await client.request("GET", "/administration/user/get_user", headers=headers, params=params)
        assert response.status_code == status.HTTP_200_OK
        response_content = json.loads(response.content.decode('utf-8'))
        assert list(response_content.keys()) == ['username', 'id', 'phone_number', 'phone_number_confirmed', 'email', 'email_confirmed', 'lockout', 'lockout_end_date_utc']
    
    async def test_successful_update_user(self, engine, client: AsyncClient):
        user_id = 1000
        await self.setup_base(engine, user_id)
        headers = {
            "access-token" : self.access_token, 
            "Content-Type": "application/x-www-form-urlencoded"
            }
        params = {"user_id": user_id, "username":"DiegoBrando"}
        response = await client.request("PUT", "/administration/user/update_user", headers=headers, data=params)
        assert response.status_code == status.HTTP_200_OK
        response_content = json.loads(response.content.decode('utf-8'))
        params = {"user_id":user_id}

        response = await client.request("GET", "/administration/user/get_user", headers=headers, params=params)
        response_content = json.loads(response.content.decode('utf-8'))
        assert response_content["username"] == "DiegoBrando"
        await self.user_repo.delete(user_id=1000)

    async def test_successful_delete_create_user(self, engine, client: AsyncClient):
        user_id = 1000
        await self.setup_base(engine, user_id)        
        headers = {
            "access-token" : self.access_token,
            "Content-Type": "application/x-www-form-urlencoded"
            }
        params = {"user_id": user_id}
        response = await client.request("DELETE", "/administration/user/delete_user", headers=headers, params=params)
        assert response.status_code == status.HTTP_200_OK

        response = await client.request("GET", "/administration/user/get_user", headers=headers, params=params)
        assert response.status_code == status.HTTP_404_NOT_FOUND

        kwargs = {
            "username":"DioBrando",
            'security_stamp': "123",
            "email":"theworld@timestop.com", 
            "phone_number":"+20-123-123-123",
            "password": "1",
            "two_factors_enabled":False,
        }
        headers = {
            'accept': 'application/json',
            "access-token" : self.access_token,
            "Content-Type": "application/x-www-form-urlencoded"
            }
        response = await client.request("POST", "/administration/user/new_user", headers=headers, data=kwargs)
        assert response.status_code == status.HTTP_200_OK
        headers = {"access-token" : self.access_token}
        response = await client.request("GET", "/administration/user/all_users", headers=headers)
        
        response_content = json.loads(response.content.decode('utf-8'))
        for user in response_content['all_users']:
            if user['username'] == 'DioBrando':
                params = {"user_id": user['id']}
                response = await client.request("DELETE", "/administration/user/delete_user", headers=headers, params=params)
                break
        else:
            raise AssertionError

    async def test_successful_groups_users(self, engine, client: AsyncClient):
        await self.setup_base(engine)
        await self.setup_groups_roles(engine)
        
        headers = {
            "access-token" : self.access_token,
            "Content-Type": "application/x-www-form-urlencoded"
            }
        data = {
            "user_id": 1000,
            "group_ids": f'{(await self.group_repo.get_group_by_name(name = "Polnareff")).id},{(await self.group_repo.get_group_by_name(name = "Silver")).id}'
            }
    
        response = await client.request("POST", "/administration/user/add_groups", headers=headers, data=data)
        assert response.status_code == status.HTTP_200_OK
        
        params = {"user_id": 1000}
        headers = {"access-token" : self.access_token}
        response = await client.request("GET", "/administration/user/show_groups", headers=headers, params=params)
        assert response.status_code == status.HTTP_200_OK
        response_content = json.loads(response.content.decode('utf-8'))
        logger.info(response_content)
        assert len(response_content['groups']) == 2

        headers = {"access-token" : self.access_token,
            "Content-Type": "application/x-www-form-urlencoded"
            }
        response = await client.request("DELETE", "/administration/user/delete_user_groups", headers=headers, data=data)
        assert response.status_code == status.HTTP_200_OK

        response = await client.request("GET", "/administration/user/show_groups", headers=headers, params=params)
        assert response.status_code == status.HTTP_200_OK
        
        response_content = json.loads(response.content.decode('utf-8'))
        logger.info(response_content)
        assert len(response_content['groups']) == 0

    async def test_successful_roles_users(self, engine, client: AsyncClient):
        await self.setup_base(engine)
        await self.setup_groups_roles(engine)
        
        headers = {
            "access-token" : self.access_token,
            "Content-Type": "application/x-www-form-urlencoded"
            }
        data = {
            "user_id": 1000,
            "role_ids": f'{(await self.role_repo.get_role_by_name(name = "Standuser")).id},{(await self.role_repo.get_role_by_name(name = "Vampire")).id}'
            }
    
        response = await client.request("POST", "/administration/user/add_roles", headers=headers, data=data)
        assert response.status_code == status.HTTP_200_OK
        
        headers = {"access-token" : self.access_token}
        params = {"user_id": 1000}
        response = await client.request("GET", "/administration/user/show_roles", headers=headers, params=params)
        assert response.status_code == status.HTTP_200_OK
        response_content = json.loads(response.content.decode('utf-8'))
        logger.info(response_content)
        assert len(response_content['roles']) == 2
        
        headers = {
            "access-token" : self.access_token,
            "Content-Type": "application/x-www-form-urlencoded"
            }
        response = await client.request("DELETE", "/administration/user/delete_user_roles", headers=headers, data=data)
        assert response.status_code == status.HTTP_200_OK

        headers = {"access-token" : self.access_token}
        response = await client.request("GET", "/administration/user/show_roles", headers=headers, params=params)
        assert response.status_code == status.HTTP_200_OK
        
        response_content = json.loads(response.content.decode('utf-8'))
        logger.info(response_content)
        a = len(response_content['roles'])
        assert a == 0

    async def test_successful_password_change(self, engine, client: AsyncClient):
        await self.setup_base(engine)
        headers = {
            "access-token" : self.access_token,
            "Content-Type": "application/x-www-form-urlencoded"
            }
        data ={
            "user_id":1000,
            "new_password": "muda_muda_muda"
        }
        password_one = (await self.user_repo.get_user_by_id(1000)).password_hash

        response = await client.request("PUT", "/administration/user/change_user_password", headers=headers, data=data)
        assert response.status_code == 200
        password_two = (await self.user_repo.get_user_by_id(1000)).password_hash
        assert password_two != password_one