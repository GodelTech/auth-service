import pytest
from fastapi import status
from httpx import AsyncClient
from src.data_access.postgresql.repositories.user import UserRepository
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any


logger = logging.getLogger(__name__)


@pytest.mark.asyncio
class TestUserEndpoint:
   
    async def test_successful_get_HTML_register_add_info(self, client: AsyncClient) -> None:
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

    async def test_successful_post_register_post_get_add_info(self, connection: AsyncSession, client: AsyncClient) -> None:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "username": "polnareff",
            "email":"polnareff@mail",
            "password":"polnareff",
            "picture":"polnareff",
            "website":"polnareff",
            "gender":"polnareff",
            }
        response = await client.request(
            "POST", "/user/register", headers=headers, data=data
        )
        assert response.status_code == status.HTTP_200_OK
        response_content = response.content.decode("utf-8")
        user_repo = UserRepository(connection)
        user = await user_repo.get_user_by_username("polnareff")
        assert '<h1>Success</h1>' in response_content

        response = await client.request(
            "GET", "/user/add_info/polnareff?scope=profile", headers=headers, data=data
        )
        assert response.status_code == status.HTTP_200_OK
        response_content = response.content.decode("utf-8")
        assert "<h1>We need to know something else</h1>" in response_content

        data = {
            "name":"polnareff",
            "given_name":"polnareff",
            "family_name":"polnareff",
            "middle_name":"polnareff",
            }
        
        response = await client.request(
            "POST", "/user/add_info/polnareff", headers=headers, data=data
        )
        assert response.status_code == status.HTTP_200_OK
        claims = await user_repo.get_claims(user.id)
        assert "family_name" in claims.keys()

    async def test_unsuccessful_post_register(self, client: AsyncClient) -> None:
                
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "username": "2polnareff",
            "email":"2polnareff@mail",
            "password":"2polnareff",
            "phone_number":"2123123132",
            }
        response = await client.request(
            "POST", "/user/register", headers=headers, data=data
        )
        assert response.status_code == status.HTTP_200_OK
        response = await client.request(
            "POST", "/user/register", headers=headers, data=data
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
        data = {
            "username": "3polnareff",
            "email":"2polnareff@mail",
            "password":"polnareff",
            "phone_number":"2123123132",
            }
        response = await client.request(
            "POST", "/user/register", headers=headers, data=data
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        data = {
            "username": "3polnareff",
            "email":"3polnareff@mail",
            "password":"polnareff",
            "phone_number":"2123123132",
            }
        response = await client.request(
            "POST", "/user/register", headers=headers, data=data
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        