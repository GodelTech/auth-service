import asyncio
import httpx

scope = (
    "gcp-api%20IdentityServerApi&grant_type="
    "password&client_id=test_client&client_secret="
    "65015c5e-c865-d3d4-3ba1-3abcb4e65500&password="
    "test_password&username=TestClient"
)
params = {
            "client_id": "test_client",
            "response_type": "code",
            "scope": scope,
            "redirect_uri": "https://www.google.com/",
        }

content_type = 'application/x-www-form-urlencoded'

async def post_to_token():
    async with httpx.AsyncClient() as client:
        r1 = await client.request("GET", 'http://127.0.0.1:8000/authorize', params=params)
        r2 = await client.request("POST", 'http://127.0.0.1:8000/token',
                                  params=params, headers={'Content-Type': content_type})
        return r1, r2

r1, r2 = asyncio.run(post_to_token())
print(r1)
print(r1.url)
print(r2)

# print(r2.json())
# print(r2.url)
# print(r2.encoding)
#
# print(r2.text)