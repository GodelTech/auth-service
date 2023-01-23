import httpx
from httpx import AsyncClient

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

async def foo():
    with httpx.AsyncClient() as client:
     r1 = await client.get('https://www.example.com/')

print(r1, sep="\n")


# r1 = httpx.get("http://127.0.0.1:8000/authorize/", params=params)
# r2 = AsyncClient.request("self", method="GET", url="http://127.0.0.1:8000/authorize/", params=params)
# r2 = httpx.get("http://127.0.0.1:8000/")
# r3 = httpx.get("https://www.python-httpx.org/")
# r4 = httpx.get('https://httpbin.org/get')

# r5 = httpx.post('https://httpbin.org/post', data={'key': 'value'})

# r6 = httpx.post("http://127.0.0.1:8000/authorize/")


