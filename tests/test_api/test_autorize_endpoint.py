import pytest
from httpx import AsyncClient

from sqlalchemy.ext.asyncio import AsyncSession


scope = 'gcp-api%20IdentityServerApi&grant_type=' \
        'password&client_id=test_client&client_secret=' \
        '65015c5e-c865-d3d4-3ba1-3abcb4e65500&password=' \
        'test_test&username=TestClient'


@pytest.mark.asyncio
async def test_successful_authorize_request(connection: AsyncSession, client: AsyncClient):
    params = {
        'client_id': 'test_client',
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': 'https://www.google.com/',
    }

    response = await client.request('GET', '/authorize/', params=params)
        
    assert response.status_code == 302
