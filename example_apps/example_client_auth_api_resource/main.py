from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware
import logging
import httpx
import requests
import jwt
import json
import requests


token_endpoint = "http://127.0.0.1:8000/token/"
client_id = "test_client" 
client_secret = "past" 
redirect_uri = "http://127.0.0.1:8888/callback/"
alarm_url_get = "http://127.0.0.1:8889/alarms/"


logging.basicConfig(level=logging.INFO)

def get_application():
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app

app = get_application()
app.add_middleware(SessionMiddleware, secret_key="123")



async def token_validation(request:Request):
    tokens = request.session.get("tokens")
    if not tokens:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No tokens")
    
    jwks_url = "http://127.0.0.1:8000/.well-known/jwks"
    jwks = requests.get(jwks_url)
    jwk = jwks.json()["keys"][0]

    # Извлечение открытого ключа
    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))
        
    access_token = tokens['access_token']
    refresh_token = tokens['refresh_token']


    try:
        # Проверяем сигнатуру access_token
        jwt.decode(jwt=access_token, key=public_key, algorithms=["RS256"], audience = 'userinfo')

        # Сигнатура верна, access_token валиден
        return

    except jwt.InvalidSignatureError:
        # Сигнатура недействительна, access_token недействителен

        # Отправляем запрос на обмен refresh_token на новый набор токенов
        token_request_data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(token_endpoint, data=token_request_data)

            if response.status_code == 200:
                token_data = response.json()
                new_access_token = token_data.get("access_token")
                # Проверяем сигнатуру нового access_token
                jwt.decode(new_access_token, jwks_url, algorithms=["RS256"], options={"verify_signature": True})

                # Обновляем access_token и refresh_token в сессии

                tokens = response.json()
                request.session["tokens"] = tokens

                return

            else:
                # Обмен refresh_token на новый набор токенов не удался
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Обмен refresh_token на новый набор токенов не удался")


oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="http://127.0.0.1:8000/authorize/",
    tokenUrl="http://127.0.0.1:8000/token/",
)


@app.get("/callback")
async def callback(request: Request, code: str):
    authorization_code = request.query_params.get("code")

    # Определите параметры тела запроса на обмен авторизационного кода на токен доступа
    token_request_data = {
        "grant_type": "authorization_code",
        "code": authorization_code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
    }

    async with httpx.AsyncClient() as client:
        # Отправьте POST-запрос на конечную точку токена доступа для обмена авторизационного кода на токен доступа
        response = await client.post(token_endpoint, data=token_request_data)
        logging.info(f"{response.status_code}\n{response.content}")
        if response.status_code == 200:
            # Успешный обмен авторизационного кода на токен доступа
            tokens = response.json()
            request.session["tokens"] = tokens
            return  RedirectResponse('/')
        else:
            # Обработка ошибки обмена авторизационного кода на токен доступа
            return JSONResponse({"error": "Ошибка обмена авторизационного кода на токен доступа"})


@app.exception_handler(HTTPException)
async def handle_auth_error(request: Request, exc: HTTPException):
    if exc.status_code == 401:
        redirect_url = "http://127.0.0.1:8000/authorize/"  # URL страницы авторизации
        redirect_params = {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,  # URL обратного вызова после авторизации
            "scope": "openid+alarm-api-resource.time.read",  # Запрашиваемые области доступа
            "state": "your_state",
        }
        redirect_url_with_params = f"{redirect_url}?{'&'.join(f'{k}={v}' for k, v in redirect_params.items())}"
        return RedirectResponse(redirect_url_with_params, status_code=302)
    
    raise exc

@app.get("/callback/access-denied",)
async def get_data():
    return {"message": f"We have not received information and permissions =("}

# Модель данных для примера
class Item(BaseModel):
    name: str
    description: str

# Защищенный маршрут, доступный только с валидным токеном
@app.get("/get_your_alarms", dependencies=[Depends(token_validation)])
async def get_data(request:Request):
    tokens = request.session.get("tokens")
    headers = {"Authorization": tokens['access_token']}
    response = requests.get(alarm_url_get, headers=headers)
    # if response.status_code != 200:
    #     raise HTTPException(status_code=response.status_code, detail="error")
    #response['message'] = 'Client app know now that: ' + response['message']
    return response


# Обычный маршрут без авторизации
@app.get("/")
async def home():
    return {"message": "Добро пожаловать на главную страницу"}

# Пример создания объекта с авторизацией
@app.post("/api/items", dependencies=[Depends(oauth2_scheme)])
async def create_item(item: Item):
    return {"message": "Объект создан", "item": item}
