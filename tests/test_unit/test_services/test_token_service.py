import jwt
import mock
import pytest
from Crypto.PublicKey.RSA import construct
from jwkest import base64_to_long
from sqlalchemy.ext.asyncio import AsyncEngine
from src.business_logic.services.jwt_token import JWTService
from src.business_logic.services import TokenService
from src.data_access.postgresql.errors import GrantNotFoundError, DeviceCodeNotFoundError
from src.data_access.postgresql.repositories import PersistentGrantRepository
from typing import Any, no_type_check
from src.presentation.api.models.tokens import BodyRequestTokenModel
from src.business_logic.services.tokens import BaseMaker, DeviceCodeMaker, CodeMaker, RefreshMaker, ClientCredentialsMaker


class MockGrant:
    def __init__(self, client_id, client_secret, flag = False) -> None:
        self.user_id = 1
        self.client_id = client_id
        self.client_secret = client_secret
        if flag:
            self.client = MockGrant(client_id=client_id, client_secret=client_secret)

@pytest.mark.asyncio
class TestTokenServices:

    async def setup_test(self) -> None:
        self.jwt = JWTService()
        self.client_id='test_client'
        self.scope='openid'
        self.grant_type="code"
        self.redirect_uri="some"
        self.client_secret="past"
        self.user_id = 1
        self.encodedattr=await self.jwt.encode_jwt(payload={'exp':1, 'payload':123})

    async def test_incorrect_grant_type_token(
            self,  
            token_service: TokenService,
        ) -> None:
        
        token_service = token_service

        for grant_type in ('mistake', '', None):
            with pytest.raises(GrantNotFoundError):
                request_body = BodyRequestTokenModel(client_id='SOME', grant_type=grant_type)
                token_service.request_model = request_body
                result = await token_service.get_tokens()
    
    async def test_incorrect_request_body(
            self,  
            token_service: TokenService,
        ) -> None:
        
        token_service = token_service

        with pytest.raises(GrantNotFoundError):
            request_body = BodyRequestTokenModel(
                client_id='SOME',
                scope='openid',
                grant_type="code", 
                redirect_uri=None,
                code=None,
                )
            token_service.request_model = request_body
            await token_service.get_tokens()

        with pytest.raises(GrantNotFoundError):
            request_body = BodyRequestTokenModel(
                client_id='SOME',
                scope='openid',
                grant_type="password", 
                username=None,
                password=None,
                )
            token_service.request_model = request_body
            await token_service.get_tokens()
        
        with pytest.raises(GrantNotFoundError):
            request_body = BodyRequestTokenModel(
                client_id='SOME',
                scope='openid',
                grant_type="refresh_token", 
                refresh_token=None,
                )
            token_service.request_model = request_body
            await token_service.get_tokens()

        with pytest.raises(GrantNotFoundError):
            request_body = BodyRequestTokenModel(
                client_id='SOME',
                scope='openid',
                grant_type="urn:ietf:params:oauth:grant-type:device_code", 
                device_code=None,
                )
            token_service.request_model = request_body
            await token_service.get_tokens()

        with pytest.raises(GrantNotFoundError):
            request_body = BodyRequestTokenModel(
                client_id='SOME',
                scope= 'openid',
                grant_type="client_credentials", 
                client_secret=None,
                )
            token_service.request_model = request_body
            await token_service.get_tokens()
    
    async def base_test_token_service(
        self,  
        token_service: TokenService,
        engine: AsyncEngine,
        grant_type:str,
    ) -> None:
        await self.setup_test()
        token_repo = PersistentGrantRepository(engine)
        if grant_type != "client_credentials":
            await token_repo.create(
                grant_data=self.encodedattr, 
                grant_type=grant_type, 
                client_id = self.client_id, 
                user_id=self.user_id
            )
        token_service = token_service
        request_body = BodyRequestTokenModel(
            client_id=self.client_id,
            scope=self.scope,
            grant_type=grant_type, 
            redirect_uri=self.redirect_uri,
            code=self.encodedattr,
            client_secret=self.client_secret,
            refresh_token=self.encodedattr,
            device_code=self.encodedattr,
            )
        token_service.request_model = request_body
        return await token_service.get_tokens()
    
    async def test_type_code(
            self,
            token_service: TokenService,
            engine: AsyncEngine,
        ):
        result = await self.base_test_token_service(
            grant_type = 'code', token_service=token_service, engine=engine)
        for param in (
            "access_token",
            "refresh_token",
            "expires_in",
            "token_type"
        ):
            assert result[param] is not None
    
    async def test_type_refresh_token(
        self,
        token_service: TokenService,
        engine: AsyncEngine,
    ):
        result = await self.base_test_token_service(
            grant_type = 'refresh_token', token_service=token_service, engine=engine)
        for param in (
            "access_token",
            "refresh_token",
            "id_token",
            "expires_in",
            "token_type"
        ):
            assert result[param] is not None    
    
    async def test_type_device_code(
        self,
        token_service: TokenService,
        engine: AsyncEngine,
    ):
        result = await self.base_test_token_service(
            grant_type = "urn:ietf:params:oauth:grant-type:device_code", token_service=token_service, engine=engine)
        for param in (
            "access_token",
            "refresh_token",
            "expires_in",
            "token_type"
        ):
            assert result[param] is not None  

    async def test_token_service_client_credentials(
        self,
        token_service: TokenService,
        engine: AsyncEngine,
    ):
        result = await self.base_test_token_service(
            grant_type = "client_credentials", token_service=token_service, engine=engine)
        for param in (
            "access_token",
            "expires_in",
            "token_type"
        ):
            assert result[param] is not None  

    async def base_test_maker(
        self,  
        token_service: TokenService,
        engine: AsyncEngine,
        grant_type:str,
        maker: BaseMaker,
        broken:bool = False
    ) -> None:
        await self.setup_test()
        token_repo = PersistentGrantRepository(engine)
        if grant_type != "client_credentials":
            await token_repo.create(
                grant_data=self.encodedattr, 
                grant_type=grant_type, 
                client_id = self.client_id, 
                user_id=self.user_id
            )
        token_service = token_service
        if broken:
            self.encodedattr = 'broken'
        request_body = BodyRequestTokenModel(
            client_id=self.client_id,
            scope=self.scope,
            grant_type=grant_type, 
            redirect_uri=self.redirect_uri,
            code=self.encodedattr,
            client_secret=self.client_secret,
            refresh_token=self.encodedattr,
            device_code=self.encodedattr,
            )
        token_service.request_model = request_body
        maker = maker(token_service)
        return await maker.create()
    
    async def test_maker_code(
            self,
            token_service: TokenService,
            engine: AsyncEngine,
        ):
        result = await self.base_test_maker(
            grant_type = 'code', token_service=token_service, engine=engine, maker = CodeMaker)
        for param in (
            "access_token",
            "refresh_token",
            "expires_in",
            "token_type"
        ):
            assert result[param] is not None
    
    async def test_maker_refresh_token(
        self,
        token_service: TokenService,
        engine: AsyncEngine,
    ):
        result = await self.base_test_maker(
            grant_type = 'refresh_token', token_service=token_service, engine=engine, maker = RefreshMaker)
        for param in (
            "access_token",
            "refresh_token",
            "id_token",
            "expires_in",
            "token_type"
        ):
            assert result[param] is not None    
    
    async def test_maker_device_code(
        self,
        token_service: TokenService,
        engine: AsyncEngine,
    ):
        result = await self.base_test_maker(
            grant_type = "urn:ietf:params:oauth:grant-type:device_code", token_service=token_service, engine=engine, maker = DeviceCodeMaker)
        for param in (
            "access_token",
            "refresh_token",
            "expires_in",
            "token_type"
        ):
            assert result[param] is not None  

    async def test_maker_client_credentials(
        self,
        token_service: TokenService,
        engine: AsyncEngine,
    ):
        result = await self.base_test_maker(
            grant_type = "client_credentials", token_service=token_service, engine=engine, maker=ClientCredentialsMaker)
        for param in (
            "access_token",
            "expires_in",
            "token_type"
        ):
            assert result[param] is not None  

    async def test_maker_device_code_broken(
        self,
        token_service: TokenService,
        engine: AsyncEngine,
    ):
        with pytest.raises(DeviceCodeNotFoundError):
            result = await self.base_test_maker(
                grant_type = "urn:ietf:params:oauth:grant-type:device_code", 
                token_service=token_service, 
                engine=engine, 
                maker = DeviceCodeMaker, 
                broken=True
            )
            
