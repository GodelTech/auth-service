from __future__ import annotations

from typing import TYPE_CHECKING, Any

from src.business_logic.authorization.service_impls import IdTokenAuthService
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
    from src.business_logic.services import JWTService, PasswordHash
    from src.data_access.postgresql.repositories import (
        ClientRepository,
        UserRepository,
    )


def _create_id_token_auth_service(
    *,
    client_repo: ClientRepository,
    user_repo: UserRepository,
    password_service: PasswordHash,
    jwt_service: JWTService,
    scope_service,
    **kwargs: Any,
) -> AuthServiceProtocol:
    return IdTokenAuthService(
        client_validator=ClientValidator(client_repo),
        redirect_uri_validator=RedirectUriValidator(client_repo),
        scope_validator=ScopeValidator(
            client_repo=client_repo,
            scope_service=scope_service
        ),
        user_credentials_validator=UserCredentialsValidator(
            user_repo=user_repo,
            password_service=password_service,
        ),
    )
