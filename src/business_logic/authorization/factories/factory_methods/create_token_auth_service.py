from __future__ import annotations

from typing import TYPE_CHECKING, Any

from src.business_logic.authorization.service_impls import TokenAuthService
from src.business_logic.authorization.validators import (
    ScopeValidator,
    UserCredentialsValidator,
)
from src.business_logic.common.validators import (
    ClientValidator,
    RedirectUriValidator,
)

if TYPE_CHECKING:
    from src.business_logic.authorization.interfaces import AuthServiceProtocol
    from src.business_logic.services import PasswordHash
    from src.data_access.postgresql.repositories import (
        ClientRepository,
        UserRepository,
    )
    from src.business_logic.jwt_manager.interfaces import JWTManagerProtocol


def _create_token_auth_service(
    *,
    client_repo: ClientRepository,
    user_repo: UserRepository,
    password_service: PasswordHash,
    jwt_manager: JWTManagerProtocol,
    **kwargs: Any,
) -> AuthServiceProtocol:
    return TokenAuthService(
        client_validator=ClientValidator(client_repo),
        redirect_uri_validator=RedirectUriValidator(client_repo),
        scope_validator=ScopeValidator(client_repo),
        user_credentials_validator=UserCredentialsValidator(
            user_repo=user_repo,
            password_service=password_service,
        ),
        user_repo=user_repo,
        jwt_manager=jwt_manager,
    )
