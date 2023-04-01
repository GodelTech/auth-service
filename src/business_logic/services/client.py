from typing import Any, Optional

from jwt.exceptions import PyJWTError

from src.data_access.postgresql.tables import Client
from src.data_access.postgresql.repositories.client import ClientRepository
from src.data_access.postgresql.repositories.persistent_grant import (
    PersistentGrantRepository,
)
from src.data_access.postgresql.repositories import ClientRepository
import secrets
from src.presentation.api.models.registration import ClientRequestModel, ClientUpdateRequestModel
from typing import Union

DEFAULT_REFRESH_TOKEN_LIFETIME = 10*60
DEFAULT_ABSOLUTE_REFRESH_TOKEN_LIFETIME = 3*60*60
DEFAULT_AUTHORIZATION_CODE_LIFETIME = 3*60*60
DEFAULT_SLIDING_REFRESH_TOKEN_LIFETIME = 3*60*60
DEFAULT_IDENTITY_TOKEN_LIFETIME = 10*60
DEFAULT_ACCESS_TOKEN_LIFETIME = 10*60


class ClientService:
    def __init__(
        self,
        client_repo: ClientRepository,
    ) -> None:
        self.client_repo = client_repo
        self.request_model:Union[ClientRequestModel, ClientUpdateRequestModel, None]

    async def generate_credentials(self):
        while True:
            client_id = secrets.token_urlsafe(16) 
            client_secret = secrets.token_urlsafe(32)
            flag = not await self.client_repo.validate_client_by_client_id(client_id=client_id)
            if flag:
                return (client_id, client_secret)
        

    async def registration(
        self,
    ) -> dict[str, Any]:
        if ',' in self.request_model.redirect_uris[0]:
            self.request_model.redirect_uris = self.request_model.redirect_uris[0].split(',')

        client_id, client_secret = await  self.generate_credentials()
        params = await self.get_params(client_id=client_id)
        await self.client_repo.create(params)
        client_id_int = (await self.client_repo.get_client_by_client_id(client_id=client_id)).id
        await self.client_repo.add_secret(client_id_int=client_id_int, value=client_secret)
        await self.client_repo.add_scope(client_id_int=client_id_int, scope=self.request_model.scope)
        await self.client_repo.add_redirect_uris(client_id_int=client_id_int, redirect_uris=self.request_model.redirect_uris)
        for grant_type in self.request_model.grant_types:
            await self.client_repo.add_grant_type(grant_type=grant_type, client_id_int=client_id_int)
        for response_type in self.request_model.response_types:
            await self.client_repo.add_response_type(client_id_int=client_id_int, response_type=response_type)
        return {
            "client_id":client_id, 
            "client_secret":client_secret
        }
    
    async def get_params(self, client_id) -> dict[str:Any]:
        refresh_token_expiration_type = "absolute"
        refresh_token_expiration_type_id = 0
        if hasattr(self.request_model, "refresh_token_expiration_type"):
            refresh_token_expiration_type_id = await self.client_repo.get_refresh_token_expiration_type_id(self.request_model.refresh_token_expiration_type)
        else:
            refresh_token_expiration_type_id = await self.client_repo.get_refresh_token_expiration_type_id(refresh_token_expiration_type)

        refresh_token_usage_type = "reuse"
        refresh_token_usage_type_id = 0
        if hasattr(self.request_model, "refresh_token_usage_type"):
            refresh_token_usage_type_id = await self.client_repo.get_refresh_token_usage_type_id(self.request_model.refresh_token_usage_type)
        else:
            refresh_token_usage_type_id = await self.client_repo.get_refresh_token_usage_type_id(refresh_token_usage_type)

        access_token_type = "jwt"
        access_token_type_id = 0
        if hasattr(self.request_model, "access_token_type"):
            access_token_type_id = await self.client_repo.get_access_token_type_id(self.request_model.access_token_type)
        else:
            access_token_type_id = await self.client_repo.get_access_token_type_id(access_token_type)

        return{
            "token_endpoint_auth_method": getattr(self.request_model, "token_endpoint_auth_method", "client_secret_post"),
            "client_id":client_id,
            "absolute_refresh_token_lifetime": getattr(self.request_model, "absolute_refresh_token_lifetime", DEFAULT_ABSOLUTE_REFRESH_TOKEN_LIFETIME),
            "access_token_lifetime": getattr(self.request_model, "access_token_lifetime", DEFAULT_ACCESS_TOKEN_LIFETIME),
            "access_token_type_id": access_token_type_id,
            "allow_access_token_via_browser": getattr(self.request_model, "allow_access_token_via_browser", True),
            "allow_offline_access": getattr(self.request_model, "allow_offline_access", False),
            "allow_plain_text_pkce" : getattr(self.request_model, "allow_plain_text_pkce", False),	
            "allow_remember_consent" : getattr(self.request_model, "allow_remember_consent", False),
            "always_include_user_claims_id_token": getattr(self.request_model, "", False), 	
            "always_send_client_claims": getattr(self.request_model, "always_send_client_claims", False),
            "authorisation_code_lifetime": getattr(self.request_model, "authorisation_code_lifetime", DEFAULT_AUTHORIZATION_CODE_LIFETIME),
            "client_name": self.request_model.client_name,
            "client_uri": self.request_model.client_uri,
            "enable_local_login": getattr(self.request_model, "enable_local_login", True),
            "enabled": getattr(self.request_model, "enabled", True), 	
            "identity_token_lifetime": int(getattr(self.request_model, "identity_token_lifetime", DEFAULT_IDENTITY_TOKEN_LIFETIME)),
            "include_jwt_id": getattr(self.request_model, "include_jwt_id", False), 	
            "logo_uri": self.request_model.logo_uri, 
            "logout_session_required": getattr(self.request_model, "logout_session_required", False),	
            "logout_uri": getattr(self.request_model, "logout_uri", 'https://www.google.com/'), 
            "prefix_client_claims": getattr(self.request_model, "prefix_client_claims", "-"),
            "protocol_type_id": 1,
            "refresh_token_expiration_type_id": refresh_token_expiration_type_id,
            "refresh_token_usage_type_id": refresh_token_usage_type_id,
            "require_client_secret": getattr(self.request_model, "require_client_secret", True),
            "require_consent": getattr(self.request_model, "require_consent", False),
            "require_pkce": getattr(self.request_model, "require_pkce", False),
            "sliding_refresh_token_lifetime": getattr(self.request_model, "sliding_refresh_token_lifetime", DEFAULT_SLIDING_REFRESH_TOKEN_LIFETIME),
            "update_access_token_claims_on_refresh": getattr(self.request_model, "update_access_token_claims_on_refresh", False),
        }
    
    async def update(
        self,
        client_id:str,
    ) -> None:
        if self.request_model.redirect_uris:
            if ',' in self.request_model.redirect_uris[0]:
                self.request_model.redirect_uris = self.request_model.redirect_uris[0].split(',')
        client = await self.client_repo.get_client_by_client_id(client_id=client_id)
        
        params ={}
        if self.request_model.client_name:
            params["client_name"] = self.request_model.client_name
        if self.request_model.client_uri:
            params["client_uri"] = self.request_model.client_uri
        if self.request_model.logo_uri:
            params["logo_uri"] = self.request_model.logo_uri
        if self.request_model.token_endpoint_auth_method:
            params["token_endpoint_auth_method"] = self.request_model.token_endpoint_auth_method

        await self.client_repo.update(client_id=client_id, **params)

        if self.request_model.response_types:
            await self.client_repo.delete_clients_response_types(client_id_int=client.id) 
            for response_type in self.request_model.response_types:
                await self.client_repo.add_response_type(client_id_int=client.id,response_type=response_type)

        if self.request_model.grant_types:
            await self.client_repo.delete_clients_grant_types(client_id_int=client.id) 
            for grant_type in self.request_model.grant_types:
                await self.client_repo.add_grant_type(client_id_int=client.id, grant_type=grant_type)

        if self.request_model.scope is not None:
            await self.client_repo.delete_scope(client_id_int=client.id)
            await self.client_repo.add_scope(client_id_int=client.id, scope=self.request_model.scope)
        if self.request_model.redirect_uris is not None:
            await self.client_repo.delete_redirect_uris(client_id_int=client.id)
            await self.client_repo.add_redirect_uris(client_id_int=client.id, redirect_uris=self.request_model.redirect_uris)

    async def get_all(self):
        clients:list[Client] = await self.client_repo.get_all()
        return [self.client_to_dict(client) for client in  clients]
    
    def client_to_dict(self, client:Client):
        return{
            "client_id":client.client_id,
            "client_name": client.client_name,
            "client_uri": client.client_uri,
            "logo_uri": client.logo_uri,
            "redirect_uris": [uri.redirect_uri for uri in client.redirect_uris],
            "grant_types": [grant_type.type_of_grant for grant_type in client.grant_types],
            "response_types": [r_type.type for r_type in client.response_types], 
            "token_endpoint_auth_method": client.token_endpoint_auth_method, 
            "scope" : client.scopes[0].scope if client.scopes else ""
        } 
    
    async def get_client_by_client_id(self, client_id):
        client:Client = await self.client_repo.get_client_by_client_id(client_id=client_id)
        return self.client_to_dict(client)