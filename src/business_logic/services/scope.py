import logging
from src.dyna_config import DOMAIN_NAME
from fastapi import Request
from typing import Any, Union
from sqlalchemy.ext.asyncio import AsyncSession
from src.data_access.postgresql.repositories.resources_related import ResourcesRepository
from src.data_access.postgresql.tables.resources_related import ApiResource, ApiScope, ApiScopeClaim, ApiScopeClaim

logger = logging.getLogger(__name__)


class ScopeService:
    def __init__(
            self,
            session:AsyncSession,
            resource_repo: ResourcesRepository,
        ) -> None:
       self.session = session
       self.resource_repo = resource_repo

    async def get_resource_api_description(self, scope:str) -> dict[str:str]:
        scope = scope.split('.')
        resource = await self.resource_repo.get_by_name(name=scope[0])
        result ={}
        for api_scope in resource.api_scope:
            if api_scope.name == scope[1]:
                for scope_claim in api_scope.api_scope_claims:
                    if scope[2]  == scope_claim.scope_claim_type.scope_claim_type:
                        result[resource.display_name] = f'{api_scope.description} : {scope_claim.scope_claim_type.scope_claim_type}'
                        return result
        
        return {'Impossible':'Error'}

    async def get_scope_description(
        self, scope:str
    ) -> list[str]:
        scope:list = scope.split(' ')
        response={'userinfo':[]}
        if not scope or 'openid' in scope:
            scope.remove('openid')
            response['userinfo'] = [
                "information from our server that does NOT include your personal data\n\tLink for details https://oidc.com/details/openid"
            ]
            if not scope:
                return response

        if 'profile' in scope:
            scope.remove('profile')
            response['userinfo'] += [
                "name",
                "given name",
                "family name",
                "middle name",
                "nickname",
                "preferred username",
                "profile",
                "picture",
                "website",
                "gender",
                "birthdate",
                "zoneinfo",
                "locale",
                "phone number and is it verified or not",
                "address",
                "profile updated last time",
            ]

        if 'email' in scope:
            scope.remove('email')
            response = response | {
                "email and is it verified or not",
            }

        dict_of_descriptions = {}
        for scope_str in scope:
            if '.' in scope_str:
                dict_answer = await self.get_resource_api_description(scope_str)
                if list(dict_answer.keys())[0] in dict_of_descriptions.keys():
                    dict_of_descriptions[list(dict_answer.keys())[0]] += dict_answer.values[0]
                else:
                    dict_of_descriptions |= dict_answer
            else:
                if scope_str not in response['userinfo']:
                    response['userinfo'].append(scope_str)
        
        result = 'Information:\n'
        for info in response['userinfo']:
            result += f'- Your {info}\n'

        result += '\nAccess to resources:'
        for n, key in enumerate(dict_of_descriptions.keys()):
            result += f'\n{n+1}. {key}:\n- {dict_of_descriptions[key]}'

        return result
 
    async def get_aud(self, scope:str = "openid") -> dict[str:str]:
        scope:list = scope.split(' ')
        aud_result = [
            "oidc.introspection.get",
            "oidc.revoke.post",
        ]

        if 'openid' in scope:
            aud_result.append("oidc.userinfo.openid")
            scope.remove('openid')
        if 'profile' in scope:
            aud_result.append("oidc.userinfo.profile")
            scope.remove('profile')
        if 'email' in scope:
            aud_result.append("oidc.userinfo.email")
            scope.remove('email')
        
        for recorde in scope:
            if '.' in recorde:
                aud_result.append(recorde)
            else:
                await self.resource_repo.get_scope_claims(resource_name='oidc', scope_name='userinfo')
                aud_result.append(f"oidc.userinfo.{recorde}")
        
        return aud_result

    async def get_all_scopes_of_resource_by_name(self, name:str) -> dict[str:str]:
        resource = await self.resource_repo.get_by_name(name=name)
        result ={}
        for api_scope in resource.api_scope:
                for scope_claim in api_scope.api_scope_claims:
                        result[f'{resource.name}.{api_scope.name}.{scope_claim.scope_claim_type.scope_claim_type}'] = api_scope.description
        return result
    