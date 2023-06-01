# import pytest
# from fastapi import status
# from httpx import AsyncClient
# from sqlalchemy import insert, exists, select
# from sqlalchemy.ext.asyncio import AsyncSession
# from src.business_logic.services.jwt_token import JWTService
# from src.data_access.postgresql.tables.persistent_grant import PersistentGrant
# import logging
# from typing import Any
# import datetime, time
# from mock import patch
# from unittest.mock import patch
# from src.business_logic.services import PasswordHash
# from src.business_logic.services.admin_auth import AdminAuthService
# from src.data_access.postgresql.tables import User
# from src.data_access.postgresql.repositories import UserRepository

# logger = logging.getLogger(__name__)


# @pytest.mark.asyncio
# class TestAdminUILogin:
#     async def test_login_success(self, connection: AsyncSession, client: AsyncClient) -> None:
#         content_type = "application/x-www-form-urlencoded"
#         data = {
#         "username" : "TestClient", 
#         "password":"test_password"
#         }
#         auth_response = await client.post(
#             "/admin/login",
#             data=data,
#             headers={"Content-Type": content_type},
#         )
#         assert auth_response.status_code == status.HTTP_302_FOUND

#     async def test_login_unsuccessful(self, connection: AsyncSession, client: AsyncClient) -> None:
#         content_type = "application/x-www-form-urlencoded"
#         data = {
#         "username" : "", 
#         "password":""
#         }
#         auth_response = await client.post(
#             "/admin/login",
#             data=data,
#             headers={"Content-Type": content_type},
#         )
#         assert auth_response.status_code == status.HTTP_400_BAD_REQUEST

#         data = {
#         "username" : "TestClient", 
#         "password" : "TestClient"
#         }
#         auth_response = await client.post(
#             "/admin/login",
#             data=data,
#             headers={"Content-Type": content_type},
#         )
#         assert auth_response.status_code == status.HTTP_400_BAD_REQUEST

#         data = {
#         "username" : "TestClient", 
#         "password" : ""
#         }
#         auth_response = await client.post(
#             "/admin/login",
#             data=data,
#             headers={"Content-Type": content_type},
#         )
#         assert auth_response.status_code == status.HTTP_400_BAD_REQUEST

#         data = {
#         "username" : "TestClient", 
#         "password" : "qweqweqwe111111111111111111111111111111111111"*10000
#         }
#         auth_response = await client.post(
#             "/admin/login",
#             data=data,
#             headers={"Content-Type": content_type},
#         )
#         assert auth_response.status_code == status.HTTP_400_BAD_REQUEST