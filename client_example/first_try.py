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
            "redirect_uri": "https://www.google.com/"
        }


async def foo():
    async with httpx.AsyncClient() as client:
        r1 = await client.request("GET", 'http://127.0.0.1:8000/authorize/', params=params)
        return r1

print(asyncio.run(foo()))


# r2 = httpx.get("http://127.0.0.1:8000/authorize/", params=params)
# print(r2)

# loop = asyncio.get_event_loop()
# loop.run_until_complete(foo())
# loop.close()


