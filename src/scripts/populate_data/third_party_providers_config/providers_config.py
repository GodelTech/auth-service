from pydantic import BaseModel
from typing import Type, ClassVar, Any


ProvidersConfigList = list[Type["IdentityProviderConfig"]]


class IdentityProviderConfig(BaseModel):
    _providers_config: ClassVar[ProvidersConfigList] = []

    name: str
    auth_endpoint_link: str
    token_endpoint_link: str
    userinfo_link: str
    internal_redirect_uri: str
    provider_icon: str

    def __init__(__pydantic_self__, **data: Any) -> None:
        super().__init__(**data)
        __pydantic_self__._providers_config.append(__pydantic_self__)
