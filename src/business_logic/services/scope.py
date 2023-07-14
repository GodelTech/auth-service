import logging
from src.dyna_config import DOMAIN_NAME
from fastapi import Request
from typing import Any, Union
from sqlalchemy.ext.asyncio import AsyncSession
from src.data_access.postgresql.repositories.resources_related import ResourcesRepository
from src.data_access.postgresql.tables.resources_related import ApiResource, ApiScope, ApiScopeClaim, ApiScopeClaim
from src.data_access.postgresql.errors import ResourceNotFoundError

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
    ) -> dict[str:Any]:
        scope:list = scope.split(' ')
        response={'Your Information':[]}
        if not scope or 'openid' in scope:
            scope.remove('openid')
            response['Your Information'] = [
                "information from our server that does NOT include your personal data\n\tLink for details https://oidc.com/details/openid"
            ]
            if not scope:
                return response
            
        if 'profile' in scope:
            scope.remove('profile')
            response['Your Information'] += [
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
            response['Your Information'] += ["email and is it verified or not"]
            
        dict_of_descriptions = {}
        for scope_str in scope:
            if '.' in scope_str:
                dict_answer = await self.get_resource_api_description(scope_str)
                if list(dict_answer.keys())[0] in dict_of_descriptions.keys():
                    dict_of_descriptions[list(dict_answer.keys())[0]] += dict_answer.values[0]
                else:
                    dict_of_descriptions |= dict_answer
            else:
                if scope_str not in response['Your Information']:
                    response['Your Information'].append(scope_str)
        
        if len(dict_of_descriptions) > 0:
            response['Access to resources'] = []
            for key in dict_of_descriptions.keys():
                response['Access to resources'] += [f'{key}\n- {dict_of_descriptions[key]}']
        return response
            
    async def get_aud(self, scope:str = "openid") -> list[str]:
        result = await self.get_full_names(scope)
        return result + [
            "oidc.introspection.get",
            "oidc.revoke.post",
        ]

    async def get_full_names(self, scope:str = "openid", userinfo_full_names:bool=False) -> list[str]:
        scope:list = scope.split(' ')
        aud_result = []
        prefix = ''
        if userinfo_full_names:
            prefix = 'oidc:userinfo:'
        if 'openid' in scope:
            aud_result.append(prefix + "openid")
            scope.remove('openid')
        if 'profile' in scope:
            aud_result.append(prefix + "profile")
            scope.remove('profile')
        if 'email' in scope:
            aud_result.append(prefix + "email")
            scope.remove('email')
        
        if len(scope)!=0:
            claim_types_userinfo = await self.resource_repo.get_scope_claims(resource_name='oidc', scope_name='userinfo')
            for recorde in scope:
                if '.' in recorde:
                    aud_result.append(recorde)
                else:
                    if recorde in claim_types_userinfo:
                        aud_result.append(f"oidc.userinfo.{recorde}")
                    else:
                        raise ValueError("Invalid scope")
        
        return aud_result

    async def get_all_scopes_of_resource_by_name(self, name:str) -> dict[str:str]:
        if not await self.resource_repo.exists_by_name(name):
            raise ResourceNotFoundError
        resource = await self.resource_repo.get_by_name(name=name)
        result ={}
        for api_scope in resource.api_scope:
            for scope_claim in api_scope.api_scope_claims:
                result[f'{resource.name}:{api_scope.name}:{scope_claim.scope_claim_type.scope_claim_type}'] = api_scope.description
        return result
    
    async def get_revoke_introspection_aud(self, name:str) -> dict[str:str]:
        if not await self.resource_repo.exists_by_name(name):
            raise ResourceNotFoundError
        resource = await self.resource_repo.get_by_name(name=name)
        result = []
        for api_scope in resource.api_scope:
            if api_scope.name == 'revoke':
                result.append(f'{resource.name}:{api_scope.name}:{str(api_scope.api_scope_claims[0].scope_claim_type)}')
            if api_scope.name == 'introspection':
                result.append(f'{resource.name}:{api_scope.name}:{str(api_scope.api_scope_claims[0].scope_claim_type)}')
        return result

    async def get_ids(self, scopes:list[str]) -> dict[str:str]:
        result = []
        for scope in scopes:
            if ':' not in scope:
                resource = await self.resource_repo.get_by_name(name='oidc')
                sub_result ={'resource_id':resource.id}
                for api_scope in resource.api_scope:
                    api_scope:ApiScope
                    if api_scope.name == 'userinfo':
                        sub_result['scope_id'] = api_scope.id
                        for scope_claim in api_scope.api_scope_claims:
                            if scope_claim.scope_claim_type.scope_claim_type == scope:
                                sub_result['claim_id'] = scope_claim.scope_claim_type.id
            else:
                scope_splited = scope.split(".")
                resource = await self.resource_repo.get_by_name(name=scope_splited[0])
                sub_result ={'resource_id':resource.id}

                for api_scope in resource.api_scope:
                        if api_scope.name == scope_splited[1]:
                            sub_result['scope_id'] = api_scope.id
                            for scope_claim in api_scope.api_scope_claims:
                                if scope_claim.scope_claim_type.scope_claim_type == scope_splited[2]:
                                    sub_result['claim_id'] = scope_claim.scope_claim_type.id
                                    break
            result.append(sub_result)
        return result
    
    async def get_all_scopes(self):
        resources = await self.resource_repo.get_all()
        result = []
        for res in resources:
            for scope in res.api_scope:
                scope:ApiScope
                for claim in scope.api_scope_claims:
                    if scope.name != 'userinfo':
                        result.append(f"{res.name}:{scope.name}:{str(claim)}")
                    else:
                        result.append(str(claim))
        return result