import logging
from src.dyna_config import DOMAIN_NAME
from fastapi import Request
from typing import Any, Union
from sqlalchemy.ext.asyncio import AsyncSession


logger = logging.getLogger(__name__)

class ScopeService:
    def __init__(
            self,
            #session:AsyncSession, 
        ) -> None:
       # self.session = session
       self.a = 1 

    def get_scope_description(
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
                "phone number",
                "phone number is verified or not",
                "address",
                "profile updated last time",
            ]

        if 'email' in scope:
            scope.remove('email')
            response = response | {
                "email",
                "email is verified or not",
            }

        result = 'Information:\n'
        for info in response['userinfo']:
            result += f'- Your {info}\n'

        return result
 